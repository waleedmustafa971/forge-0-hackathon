"""GitHub-facing evidence reports: the pull-request description and the issue comment.

They are condensed from :func:`services.reports.build_report`: what was considered, what the
experiments showed, which explanations were ruled out, and how the patch was verified. The full
report is attached to the CI run as an artifact.
"""

from __future__ import annotations

from typing import Any

GITHUB_BODY_LIMIT = 60_000  # GitHub rejects bodies over 65,536 characters
MARK = {True: "✔", False: "✘", None: "·"}


def _hypotheses(report: dict[str, Any]) -> list[str]:
    lines = [
        "| | Explanation | Prior → final confidence | Status |",
        "|---|---|---|---|",
    ]
    for h in report["hypotheses"]:
        lines.append(
            f"| {h['key']} | {h['title']} | {h['prior']:.2f} → **{h['confidence']:.2f}** | {h['status']} |"
        )
    return lines


def _experiments(report: dict[str, Any]) -> list[str]:
    lines = []
    for e in report["experiments"]:
        ev = e.get("evaluation") or {}
        verdicts = ", ".join(f"{MARK[p['matched']]} {p['hypothesis']}" for p in ev.get("predictions") or [])
        detail = str(ev.get("detail") or "").replace("\n", " ")[:220]
        lines.append(
            f"- **{e['key']}** ({e['kind']}, {str(e['outcome']).upper()}): {e['objective']}"
            + (f" — {detail}" if detail else "")
            + (f" — predictions: {verdicts}" if verdicts else "")
        )
    return lines


def _verification(patch: dict[str, Any]) -> list[str]:
    v = patch.get("verification") or {}
    base, after = v.get("baseline_summary") or {}, v.get("patched_summary") or {}
    lines = [f"**{v.get('verdict', 'unverified')}** — " + "; ".join(v.get("reasons") or [])]
    if base or after:
        lines.append(
            f"- Suite before: {base.get('passed', 0)}/{base.get('total', 0)} passing · "
            f"after: {after.get('passed', 0)}/{after.get('total', 0)} passing"
        )
    if v.get("target_repeat_runs"):
        lines.append(f"- Target re-runs after the patch: {', '.join(v['target_repeat_runs'])}")
    if v.get("fixed"):
        lines.append("- Fixed: " + ", ".join(f"`{t}`" for t in v["fixed"]))
    lines.append("- Regressions: " + (", ".join(f"`{t}`" for t in v["regressions"]) or "none"))
    return lines


def _header(report: dict[str, Any]) -> list[str]:
    target = report.get("target_failure") or {}
    prov = report["provider"]
    lines = [
        f"**Failing test:** `{target.get('test_name', 'unknown')}` in `{target.get('file', '?')}`",
        f"**Verdict:** {report['investigation']['verdict_text']}",
        f"**Model:** {prov['name']} / {prov['model']}" + (" (**SIMULATED**)" if prov["simulated"] else ""),
    ]
    flakiness = ((report.get("experiments") or [{}])[0].get("evaluation") or {}).get("flakiness")
    if flakiness:
        lines.append(f"**Re-runs:** {flakiness['summary']}")
    if prov.get("disclaimer"):
        lines += ["", f"> {prov['disclaimer']}"]
    return lines


def _footer(report: dict[str, Any]) -> list[str]:
    usage = report.get("usage") or {}
    return [
        "",
        "<sub>FORGE-0 · "
        f"{usage.get('model_calls', 0)} model calls · {usage.get('experiments', 0)} experiments · "
        f"{usage.get('sandbox_runs', 0)} sandbox runs · "
        f"~${float(usage.get('estimated_cost_usd') or 0):.2f} · "
        "the full evidence report is attached to the workflow run.</sub>",
    ]


def _limit(text: str) -> str:
    if len(text) <= GITHUB_BODY_LIMIT:
        return text
    return text[: GITHUB_BODY_LIMIT - 200] + "\n\n_… truncated; see the full report artifact._\n"


def render_pr_body(report: dict[str, Any]) -> str:
    patch = next(p for p in report["patches"] if p["key"] == report["proposed_fix"])
    lines = ["## FORGE-0 verified fix", "", *_header(report), ""]
    lines += ["### Root cause", "", report.get("root_cause") or "_Not established._", ""]
    lines += ["### The fix", "", patch["summary"], "", patch["rationale"], ""]
    if report["hypotheses"]:
        lines += ["### Explanations considered", "", *_hypotheses(report), ""]
    if report["experiments"]:
        lines += ["### Experiments run in the sandbox", "", *_experiments(report), ""]
    lines += ["### Independent verification", "", *_verification(patch), ""]
    if patch.get("diff"):
        lines += [
            "<details><summary>Diff</summary>",
            "",
            "```diff",
            patch["diff"].rstrip(),
            "```",
            "</details>",
        ]
    lines += [
        "",
        "> FORGE-0 proposes; a human decides. Review the evidence and the diff before merging.",
        *_footer(report),
    ]
    return _limit("\n".join(lines) + "\n")


def render_issue_comment(report: dict[str, Any]) -> str:
    lines = ["## FORGE-0 investigation", "", *_header(report), ""]
    lines += [
        "FORGE-0 did **not** find a patch that passes independent verification, so it is not opening a "
        "pull request. This is what the evidence shows so far:",
        "",
    ]
    if report.get("root_cause"):
        lines += ["### Leading explanation", "", report["root_cause"], ""]
    if report["hypotheses"]:
        lines += ["### Explanations considered", "", *_hypotheses(report), ""]
    if report["experiments"]:
        lines += ["### Experiments run in the sandbox", "", *_experiments(report), ""]
    rejected = [p for p in report["patches"] if p["status"] in ("rejected", "apply_failed")]
    if rejected:
        lines += ["### Patches the verifier rejected", ""]
        for p in rejected:
            reasons = "; ".join((p.get("verification") or {}).get("reasons") or [])
            lines.append(f"- **{p['key']}** {p['summary']} — {reasons}")
        lines.append("")
    lines += _footer(report)
    return _limit("\n".join(lines) + "\n")


def pr_title(report: dict[str, Any]) -> str:
    patch = next(p for p in report["patches"] if p["key"] == report["proposed_fix"])
    target = (report.get("target_failure") or {}).get("test_name", "failing test")
    title = f"FORGE-0: {patch['summary']}"
    return title if len(title) <= 120 else f"FORGE-0: fix `{target}`"[:120]
