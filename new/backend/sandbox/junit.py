"""Parses the JUnit XML report that pytest writes to stdout in the sandbox.

Test names follow the node:test convention (``tests/test_x.py > TestClass > test_a``) so the
rest of FORGE-0 (leaf-name matching, isolation patterns) works unchanged for both runners.
Traceback paths are anchored at ``/work/`` like the container paths node reports.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET  # noqa: S405 - parses the sandbox's own pytest report

from core.schemas import TestCaseResult, TestRunSummary

_REPORT = re.compile(r"<\?xml[^>]*\?>\s*<testsuites.*?</testsuites>", re.DOTALL)
_TB_PATH = re.compile(r"^(?P<path>[\w./-]+\.py):(?P<line>\d+):", re.MULTILINE)
_ERROR_NAME = re.compile(r"^(?:E\s+)?(?P<name>[A-Za-z_][\w.]*(?:Error|Exception|Failed|Exit))\b")


def _name(case: ET.Element) -> tuple[str, str | None]:
    file = case.get("file")
    classname = case.get("classname") or ""
    parts: list[str] = []
    if file:
        module = file.removesuffix(".py").replace("/", ".")
        rest = classname[len(module) :].lstrip(".") if classname.startswith(module) else ""
        parts = [file, *[p for p in rest.split(".") if p]]
    elif classname:
        parts = [classname]
    return " > ".join([*parts, case.get("name") or "?"]), file


def _error_name(message: str, text: str) -> str | None:
    for candidate in [message, *reversed(text.splitlines())]:
        match = _ERROR_NAME.match(candidate.strip())
        if match:
            return match.group("name").rsplit(".", 1)[-1]
    # pytest reports a bare `assert` by its rewritten expression ("assert -1 == 5").
    return "AssertionError" if message.startswith("assert ") else None


def parse_junit(output: str) -> TestRunSummary:
    match = _REPORT.search(output)
    if not match:
        return TestRunSummary(parse_ok=False)
    try:
        root = ET.fromstring(match.group(0))  # noqa: S314 - trusted, produced by our own runner
    except ET.ParseError:
        return TestRunSummary(parse_ok=False)
    results: list[TestCaseResult] = []
    for case in root.iter("testcase"):
        name, file = _name(case)
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        problem = failure if failure is not None else error
        status = "failed" if problem is not None else ("skipped" if skipped is not None else "passed")
        message = text = ""
        if problem is not None:
            message = (problem.get("message") or "").strip()
            text = problem.text or ""
        line = case.get("line")
        results.append(
            TestCaseResult(
                name=name,
                file=file,
                status=status,  # type: ignore[arg-type]
                duration_ms=float(case.get("time") or 0) * 1000,
                failure_type=None
                if problem is None
                else ("testCodeFailure" if failure is not None else "hookFailed"),
                error=message[:4000] or None,
                error_name=_error_name(message, text) if problem is not None else None,
                stack=_TB_PATH.sub(r"/work/\g<path>:\g<line>:", text)[:8000] or None,
                location=f"/work/{file}:{int(line) + 1}" if file and line and line.isdigit() else None,
            )
        )
    summary = TestRunSummary(tests=results, parse_ok=True)
    summary.total = len(results)
    summary.passed = sum(1 for r in results if r.status == "passed")
    summary.failed = sum(1 for r in results if r.status == "failed")
    summary.skipped = sum(1 for r in results if r.status == "skipped")
    return summary
