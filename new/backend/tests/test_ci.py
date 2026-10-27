import subprocess

from agents.orchestrator import Orchestrator
from cli.ci import Shell, branch_name, open_pull_request, parse_issue, write_reports
from core.database import session_scope
from core.models import Investigation, Repository
from services.repo_analysis import profile_repository
from services.reports import build_report
from tests.fakes import TARGET, FakeSandbox


def test_issue_text_names_the_failing_test():
    test, symptom = parse_issue(
        "Cancelled orders can be paid\n\nFailing test: `does not allow a cancelled order`\n"
    )
    assert test == "does not allow a cancelled order"
    assert symptom.startswith("Cancelled orders can be paid")
    assert parse_issue("no test named here")[0] is None


def test_branch_names_are_safe_and_unique_per_investigation():
    name = branch_name("order status lifecycle > does not allow a cancelled order", "0123456789abcdef")
    assert name == "forge0/fix-does-not-allow-a-cancelled-order-01234567"


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


class RecordingShell(Shell):
    """Runs git for real but records gh, which would need GitHub."""

    def __init__(self, cwd):
        super().__init__(cwd, dry_run=False)
        self.gh: list[list[str]] = []

    def __call__(self, *cmd):
        if cmd[0] == "gh":
            self.gh.append(list(cmd))
            return "https://github.com/acme/shop/pull/7"
        return super().__call__(*cmd)


def investigate(demo_copy, sandbox):
    with session_scope() as db:
        repo = Repository(
            name="shop",
            source_type="local",
            source=str(demo_copy),
            snapshot_path=str(demo_copy),
            profile=profile_repository(demo_copy),
        )
        db.add(repo)
        db.flush()
        inv = Investigation(
            repository_id=repo.id, title="ci", target_test=TARGET, mode="forge", usage={}, budget={}
        )
        db.add(inv)
        db.flush()
        inv_id = inv.id
    Orchestrator(inv_id, sandbox=sandbox).run()
    with session_scope() as db:
        return build_report(db, db.get(Investigation, inv_id))


def test_verified_fix_is_committed_pushed_and_proposed_with_its_evidence(demo_copy, tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    git(demo_copy, "init", "-q", "-b", "main")
    git(demo_copy, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    git(demo_copy, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "initial")
    git(demo_copy, "remote", "add", "origin", str(remote))
    report = investigate(demo_copy, FakeSandbox())
    assert report["proposed_fix"] == "P1"

    paths = write_reports(report, tmp_path / "out")
    body = paths["pr_body"].read_text(encoding="utf-8")
    assert "## FORGE-0 verified fix" in body and "### Independent verification" in body
    assert "### Explanations considered" in body and "refuted" in body
    assert "```diff" in body and "allowed.length === 0" in body

    sh = RecordingShell(demo_copy)
    url = open_pull_request(report, demo_copy, "main", paths["pr_body"], sh)
    assert url.endswith("/pull/7")
    branch = branch_name(TARGET, report["investigation"]["id"])
    assert git(demo_copy, "rev-parse", "--abbrev-ref", "HEAD") == branch
    assert git(demo_copy, "log", "-1", "--format=%an") == "forge0[bot]"
    assert git(demo_copy, "show", "--name-only", "--format=", "HEAD") == "src/domain/status.ts"
    assert "allowed.length === 0 ||" not in (demo_copy / "src/domain/status.ts").read_text(encoding="utf-8")
    assert branch in git(remote, "branch", "--list", branch)
    [pr] = sh.gh
    assert pr[:3] == ["gh", "pr", "create"]
    assert pr[pr.index("--base") + 1] == "main" and pr[pr.index("--head") + 1] == branch
    assert pr[pr.index("--body-file") + 1] == str(paths["pr_body"])


def test_unverified_investigations_produce_an_issue_comment_instead(demo_copy, tmp_path):
    report = investigate(demo_copy, FakeSandbox(break_regression=True))
    paths = write_reports(report, tmp_path / "out")
    assert "pr_body" not in paths
    comment = paths["comment"].read_text(encoding="utf-8")
    assert "did **not** find a patch that passes independent verification" in comment
    assert "### Patches the verifier rejected" in comment and "records separate charges" in comment
