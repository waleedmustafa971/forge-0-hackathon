"""`forge0-ci`: investigate a failing test in a checked-out repository and report on GitHub.

    forge0-ci --repo . [--test NAME] [--issue-body-file FILE] [--report-dir DIR]
              [--open-pr --base main] [--comment-issue N] [--dry-run]

Runs a full FORGE-0 investigation headlessly (temporary SQLite database, real Docker sandbox),
writes the evidence report, and then:

* verified fix + ``--open-pr``: applies the verified patch to the working tree, commits it on a
  ``forge0/...`` branch, pushes it and opens a pull request whose description is the evidence;
* otherwise + ``--comment-issue``: comments the evidence (and why no PR was opened) on the issue.

GitHub calls go through the `gh` CLI, authenticated by ``GH_TOKEN`` (e.g. the workflow's token).
``--dry-run`` prints the git and gh commands instead of running them. The investigation itself is
never skipped: it uses the provider configured by ``AI_PROVIDER`` and friends.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

BOT_NAME = "forge0[bot]"
BOT_EMAIL = "forge0-bot@users.noreply.github.com"
_TEST_LINE = re.compile(
    r"^\s*(?:failing\s+)?test\s*:\s*`?(?P<name>[^`\n]+?)`?\s*$", re.IGNORECASE | re.MULTILINE
)


def parse_issue(text: str) -> tuple[str | None, str]:
    """Returns (failing test named in the issue, symptom text) from an issue title + body."""
    match = _TEST_LINE.search(text)
    return (match.group("name").strip() if match else None), text.strip()[:2000]


def branch_name(test: str | None, investigation_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (test or "failing-test").split(" > ")[-1].lower()).strip("-")[:40]
    return f"forge0/fix-{slug or 'test'}-{investigation_id[:8]}"


class Shell:
    """Runs (or, in dry-run mode, records) git and gh commands in the repository."""

    def __init__(self, cwd: Path, dry_run: bool) -> None:
        self.cwd = cwd
        self.dry_run = dry_run
        self.commands: list[list[str]] = []

    def __call__(self, *cmd: str) -> str:
        self.commands.append(list(cmd))
        if self.dry_run:
            print("[dry-run] " + shlex.join(cmd))
            return ""
        done = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True, check=False)  # noqa: S603
        if done.returncode != 0:
            raise RuntimeError(f"{shlex.join(cmd)} failed: {done.stderr.strip()[:500]}")
        return done.stdout.strip()


def _configure_environment(repo: Path, workdir: Path) -> None:
    """Points the backend at throwaway state and lets it import `repo` (before any backend import)."""
    os.environ["DATABASE_URL"] = f"sqlite:///{(workdir / 'forge0.db').as_posix()}"
    os.environ["DATA_DIR"] = str(workdir / "data")
    roots = [p for p in os.environ.get("IMPORT_ALLOWED_ROOTS", "").split(",") if p.strip()]
    os.environ["IMPORT_ALLOWED_ROOTS"] = ",".join([*roots, str(repo)])
    os.environ.setdefault("SEED_DEMO", "false")
    os.environ.setdefault("LOG_LEVEL", "WARNING")
    os.environ.setdefault("LOG_FORMAT", "text")


def investigate(repo: Path, test: str | None, symptom: str, mode: str) -> dict[str, Any]:
    from agents.orchestrator import Orchestrator
    from core.config import get_settings
    from core.database import init_db, session_scope
    from core.logging import configure_logging
    from core.models import Investigation
    from sandbox.docker import WslKeepAlive, get_sandbox
    from services.reports import build_report
    from services.repositories import import_local

    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)
    init_db()
    keepalive = WslKeepAlive(get_sandbox().docker)
    keepalive.start()
    try:
        with session_scope() as db:
            record = import_local(db, str(repo), name=repo.name)
            inv = Investigation(
                repository_id=record.id,
                title=f"[ci] {test or 'first failing test'}",
                symptom=symptom,
                target_test=test,
                mode=mode,
                usage={},
                budget={},
            )
            db.add(inv)
            db.flush()
            inv_id = inv.id
        Orchestrator(inv_id).run()
        with session_scope() as db:
            inv = db.get(Investigation, inv_id)
            assert inv is not None
            return build_report(db, inv)
    finally:
        keepalive.stop()


def write_reports(report: dict[str, Any], out: Path) -> dict[str, Path]:
    from services.pr_report import render_issue_comment, render_pr_body
    from services.reports import render_markdown

    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": out / "forge0-report.json",
        "markdown": out / "forge0-report.md",
        "comment": out / "forge0-comment.md",
    }
    paths["json"].write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    paths["markdown"].write_text(render_markdown(report), encoding="utf-8")
    paths["comment"].write_text(render_issue_comment(report), encoding="utf-8")
    if report.get("proposed_fix"):
        paths["pr_body"] = out / "forge0-pr.md"
        paths["pr_body"].write_text(render_pr_body(report), encoding="utf-8")
    return paths


def open_pull_request(report: dict[str, Any], repo: Path, base: str, body: Path, sh: Shell) -> str:
    from core.schemas import SourceEdit
    from services.pr_report import pr_title
    from services.workspace import apply_edits

    patch = next(p for p in report["patches"] if p["key"] == report["proposed_fix"])
    test = (report.get("target_failure") or {}).get("test_name")
    branch = branch_name(test, report["investigation"]["id"])
    edits = [SourceEdit(**e) for e in _patch_edits(report, patch["key"])]
    sh("git", "checkout", "-b", branch)
    if not sh.dry_run:
        apply_edits(repo, edits, allow_test_files=False, allow_create=True)
    sh("git", "add", "--", *[f["path"] for f in patch["files_changed"]])
    trailer = f"Verified by FORGE-0 investigation {report['investigation']['id']}."
    sh(
        "git", "-c", f"user.name={BOT_NAME}", "-c", f"user.email={BOT_EMAIL}",
        "commit", "-m", pr_title(report), "-m", trailer,
    )  # fmt: skip
    sh("git", "push", "--set-upstream", "origin", branch)
    url = sh(
        "gh",
        "pr",
        "create",
        "--base",
        base,
        "--head",
        branch,
        "--title",
        pr_title(report),
        "--body-file",
        str(body),
    )
    return url or f"(dry-run) PR from {branch} into {base}"


def _patch_edits(report: dict[str, Any], key: str) -> list[dict[str, Any]]:
    from core.database import session_scope
    from core.models import Patch

    with session_scope() as db:
        row = db.query(Patch).filter_by(investigation_id=report["investigation"]["id"], key=key).one()
        return list(row.edits)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="checked-out repository (default: cwd)")
    parser.add_argument("--test", help="failing test to investigate (default: the first failing test)")
    parser.add_argument("--symptom", default="", help="free-text description of the problem")
    parser.add_argument(
        "--issue-body-file", type=Path, help="issue title + body; may name `Failing test: ...`"
    )
    parser.add_argument("--mode", choices=["forge", "iterative", "baseline"], default="forge")
    parser.add_argument("--report-dir", type=Path, default=Path("forge0-report"))
    parser.add_argument("--open-pr", action="store_true", help="open a PR when a fix is verified")
    parser.add_argument("--base", default="main", help="base branch for the pull request")
    parser.add_argument("--comment-issue", type=int, help="issue to comment on when no fix is verified")
    parser.add_argument(
        "--dry-run", action="store_true", help="print git/gh commands instead of running them"
    )
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    test, symptom = args.test, args.symptom
    if args.issue_body_file:
        named, text = parse_issue(args.issue_body_file.read_text(encoding="utf-8"))
        test, symptom = test or named, symptom or text

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with tempfile.TemporaryDirectory(prefix="forge0-ci-", ignore_cleanup_errors=True) as tmp:
        _configure_environment(repo, Path(tmp))
        try:
            return _investigate_and_publish(args, repo, test, symptom)
        finally:
            from core.database import get_engine

            get_engine().dispose()  # release the SQLite file so the temporary directory can go


def _investigate_and_publish(args: argparse.Namespace, repo: Path, test: str | None, symptom: str) -> int:
    report = investigate(repo, test, symptom, args.mode)
    paths = write_reports(report, args.report_dir)
    verdict = report["investigation"]["verdict"]
    print(f"FORGE-0 verdict: {verdict} — {report['investigation']['verdict_text']}")
    print(f"Evidence report: {paths['markdown']}")
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as handle:
            handle.write((paths.get("pr_body") or paths["comment"]).read_text(encoding="utf-8"))
    sh = Shell(repo, args.dry_run)
    try:
        if report.get("proposed_fix") and args.open_pr:
            if args.comment_issue:
                with paths["pr_body"].open("a", encoding="utf-8") as handle:
                    handle.write(f"\nCloses #{args.comment_issue}\n")
            url = open_pull_request(report, repo, args.base, paths["pr_body"], sh)
            print(f"Pull request: {url}")
            if args.comment_issue:
                note = f"FORGE-0 opened {url} with a verified fix; the evidence is in its description."
                sh("gh", "issue", "comment", str(args.comment_issue), "--body", note)
        elif args.comment_issue:
            sh("gh", "issue", "comment", str(args.comment_issue), "--body-file", str(paths["comment"]))
            print(f"Commented on issue #{args.comment_issue}")
    except RuntimeError as exc:
        print(f"GitHub step failed: {exc}", file=sys.stderr)
        return 1
    if report["investigation"]["status"] == "failed":
        print(f"Investigation failed: {report['investigation']['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
