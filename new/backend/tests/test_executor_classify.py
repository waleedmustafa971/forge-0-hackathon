from agents.executor import classify, is_runtime_failure, observation_text
from core.schemas import ExecutionResult
from core.schemas import TestCaseResult as CaseResult
from core.schemas import TestRunSummary as RunSummary


def result(*tests: CaseResult) -> ExecutionResult:
    failed = sum(t.status == "failed" for t in tests)
    run = RunSummary(tests=list(tests), total=len(tests), passed=len(tests) - failed, failed=failed)
    return ExecutionResult(
        runner="node_test", image="node", command=[], exit_code=1, duration_ms=5, test_run=run
    )


def failing(failure_type: str) -> CaseResult:
    return CaseResult(
        name="probe",
        status="failed",
        failure_type=failure_type,
        error="Carrier rejected shipment for SKU-MONITOR",
        error_name="CarrierUnavailableError",
    )


def test_runtime_failure_is_flagged_in_the_detail_and_the_observed_output():
    res = result(failing("unhandledRejection"))
    outcome, detail = classify(res, ["test/forge-experiments/E1.test.ts"])
    assert outcome == "fail" and is_runtime_failure(res)
    assert "by the runtime (unhandledRejection" in detail
    assert "probe [unhandledRejection]: CarrierUnavailableError" in observation_text(res)


def test_assertion_failures_are_not_runtime_failures():
    res = result(failing("testCodeFailure"), failing("unhandledRejection"))
    outcome, detail = classify(res, [])
    assert outcome == "fail" and not is_runtime_failure(res)
    assert detail == "2 of 2 executed tests failed"
