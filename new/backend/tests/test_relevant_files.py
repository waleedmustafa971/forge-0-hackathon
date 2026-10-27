import json

import pytest

from core.config import REPO_ROOT
from services.repo_analysis import collect_relevant_files

DEMO = REPO_ROOT / "demo" / "order-management"
DEFECT_DIRS = sorted(d for d in (REPO_ROOT / "demo" / "defects").iterdir() if d.is_dir())


@pytest.mark.parametrize("defect_dir", DEFECT_DIRS, ids=lambda p: p.name)
def test_root_cause_files_survive_the_file_budget(defect_dir):
    # app.ts imports every service, so a plain breadth-first walk from the failing test fills the
    # budget with whatever app.ts imports first and drops the code under test.
    defect = json.loads((defect_dir / "defect.json").read_text(encoding="utf-8"))
    files = collect_relevant_files(DEMO, [(defect["failing_test"]["file"], "failing test file")])
    paths = [f.path for f in files]
    assert len(paths) <= 14
    # Data read at runtime (D10's config/fees.json) is never imported, so it is never collected:
    # agents only learn its contents by running code.
    sources = {f for f in defect["relevant_files"] if not f.endswith(".json")}
    assert sources <= set(paths)


def test_named_files_and_their_imports_come_first(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    for i in range(20):
        (src / f"a{i:02d}.ts").write_text(f"export const a{i} = {i};\n")
    (src / "target.ts").write_text("import { helper } from './zhelper.ts';\nexport const target = helper;\n")
    (src / "zhelper.ts").write_text("export const helper = 1;\n")
    imports = "".join(f"import {{ a{i} }} from './a{i:02d}.ts';\n" for i in range(20))
    wiring = "import { target } from './target.ts';\nexport const app = { target };\n"
    (src / "app.ts").write_text(imports + wiring)
    (tmp_path / "case.test.ts").write_text(
        "import { app } from './src/app.ts';\nasync function run() { return app.target; }\n"
    )
    seeds = [("case.test.ts", "failing test file")]
    paths = [f.path for f in collect_relevant_files(tmp_path, seeds, max_files=5)]
    assert paths[:3] == ["case.test.ts", "src/app.ts", "src/target.ts"]
    assert "src/zhelper.ts" in paths


def test_python_imports_are_followed_for_flat_and_src_layouts(tmp_path):
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("from .core import run\n")
    (tmp_path / "src" / "pkg" / "core.py").write_text("from . import util\n\ndef run():\n    return util.x\n")
    (tmp_path / "src" / "pkg" / "util.py").write_text("x = 1\n")
    (tmp_path / "tests" / "test_pkg.py").write_text(
        "from pkg import run\n\ndef test_run():\n    assert run()\n"
    )
    seeds = [("tests/test_pkg.py", "failing test file")]
    paths = [f.path for f in collect_relevant_files(tmp_path, seeds)]
    assert paths == ["tests/test_pkg.py", "src/pkg/__init__.py", "src/pkg/core.py", "src/pkg/util.py"]
