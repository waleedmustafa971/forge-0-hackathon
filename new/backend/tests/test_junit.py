from sandbox.junit import parse_junit

REPORT = """collected 3 items
tests/test_calc.py .FE
<?xml version="1.0" encoding="utf-8"?><testsuites>
<testsuite name="pytest" errors="1" failures="1" skipped="0" tests="3">
<testcase classname="tests.test_calc" name="test_mul" file="tests/test_calc.py" line="2" time="0.001" />
<testcase classname="tests.test_calc.TestAdd" name="test_add[2-3]" file="tests/test_calc.py" line="6"
 time="0.002">
<failure message="AssertionError: negative">tests/test_calc.py:7: in test_add
    assert add(2, 3) == 5
calc/__init__.py:5: in check
    assert x &gt; 0, 'negative'
E   AssertionError: negative</failure></testcase>
<testcase classname="tests.test_calc" name="test_db" file="tests/test_calc.py" line="9" time="0">
<error message="failed on setup with &quot;ValueError: no db&quot;">E   ValueError: no db</error></testcase>
</testsuite></testsuites>
1 failed, 1 passed, 1 error in 0.02s
"""


def test_parses_pytest_junit_into_node_style_names_and_container_paths():
    run = parse_junit(REPORT)
    assert run.parse_ok and (run.total, run.passed, run.failed) == (3, 1, 2)
    mul, add, db = run.tests
    assert mul.name == "tests/test_calc.py > test_mul" and mul.status == "passed"
    assert add.name == "tests/test_calc.py > TestAdd > test_add[2-3]"
    assert add.error_name == "AssertionError" and add.failure_type == "testCodeFailure"
    assert "/work/calc/__init__.py:5:" in add.stack and add.location == "/work/tests/test_calc.py:7"
    assert db.status == "failed" and db.failure_type == "hookFailed" and db.error_name == "ValueError"


def test_bare_assert_is_an_assertion_error_and_missing_reports_do_not_parse():
    report = REPORT.replace('message="AssertionError: negative"', 'message="assert -1 == 5"')
    assert parse_junit(report).tests[1].error_name == "AssertionError"
    assert not parse_junit("ImportError while loading conftest").parse_ok
