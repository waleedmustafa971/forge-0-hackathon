from agents.investigator import classify_flakiness


def test_failing_every_isolated_run_is_deterministic():
    report = classify_flakiness(["failed", "failed", "failed"], None, "test/a.test.ts")
    assert report.classification == "deterministic"


def test_failing_some_isolated_runs_is_intermittent():
    report = classify_flakiness(["failed", "passed", "failed"], None, "test/a.test.ts")
    assert report.classification == "intermittent"
    assert "2/3" in report.summary


def test_passing_alone_but_failing_with_its_file_is_order_dependent_within_the_file():
    report = classify_flakiness(["passed"] * 3, "failed", "test/loyalty.test.ts")
    assert report.classification == "order_dependent"
    assert "test/loyalty.test.ts" in report.summary and "earlier test in that file" in report.summary


def test_passing_with_its_file_points_at_other_test_files():
    report = classify_flakiness(["passed"] * 3, "passed", "test/a.test.ts")
    assert report.classification == "order_dependent"
    assert "other test files" in report.summary


def test_unparseable_runs_are_unknown():
    assert classify_flakiness(["error", "missing", "error"], "error", "t").classification == "unknown"
