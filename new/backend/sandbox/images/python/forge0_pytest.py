"""pytest plugin baked into the FORGE-0 Python sandbox image.

``--forge0-pattern=REGEX`` keeps only tests whose name or node id matches the regular expression,
so a test-name pattern means the same for pytest as ``--test-name-pattern`` does for node:test
(``-k`` takes a boolean expression, not a regex).
"""

import re


def pytest_addoption(parser):
    parser.addoption("--forge0-pattern", default=None, help="regex selecting tests by name or node id")


def pytest_collection_modifyitems(config, items):
    pattern = config.getoption("--forge0-pattern")
    if not pattern:
        return
    regex = re.compile(pattern)
    keep = [item for item in items if regex.search(item.name) or regex.search(item.nodeid)]
    dropped = [item for item in items if item not in keep]
    if dropped:
        config.hook.pytest_deselected(items=dropped)
        items[:] = keep
