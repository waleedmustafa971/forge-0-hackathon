"""Assemble a runnable FORGE-0: the pre-hackathon core plus the hackathon work in this repository.

    python assemble.py                     # clones the core from GitHub into ./forge-0
    python assemble.py --core PATH --out DIR

Steps: clone the core, check out the commit whose tree is the Oct 19 core, apply every patch in
patches/ (changes to pre-existing files), copy new/ (files created during the hackathon) on top,
and check that the result is byte-for-byte the tree FORGE-0 was built and benchmarked from.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

CORE_URL = "https://github.com/waleedmustafa971/forge-0-core.git"
CORE_TREE = "2b92b06020c31a745a6a63678b335eaf0651bf94"  # git tree of the pre-hackathon core (Oct 19, 2026)
RESULT_TREE = "a66e3d98fa59bb7f5710d70f6f3f27172dc8697b"  # git tree of core + hackathon work
HERE = Path(__file__).resolve().parent
IDENTITY = ["-c", "user.name=assemble.py", "-c", "user.email=assemble@localhost"]


def git(*args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--core", default=CORE_URL, help="core repository URL or path")
    parser.add_argument("--out", default="forge-0", help="directory to create")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    if out.exists():
        sys.exit(f"{out} already exists")
    subprocess.run(["git", "clone", "--quiet", args.core, str(out)], check=True)
    git("config", "core.autocrlf", "false", cwd=out)

    commits = git("rev-list", "--all", cwd=out).split()
    base = next((c for c in commits if git("rev-parse", f"{c}^{{tree}}", cwd=out) == CORE_TREE), None)
    if base is None:
        sys.exit("No commit in the core repository has the expected pre-hackathon tree")
    git("checkout", "--quiet", "-b", "assembled", base, cwd=out)

    # Apply to the index, then write it out, so local line-ending settings cannot reject a patch.
    patches = sorted(str(p) for p in (HERE / "patches").rglob("*.patch"))
    git("apply", "--cached", *patches, cwd=out)
    git("checkout", "--", ".", cwd=out)

    new_files = sorted(p.relative_to(HERE / "new") for p in (HERE / "new").rglob("*") if p.is_file())
    shutil.copytree(HERE / "new", out, dirs_exist_ok=True)
    git("add", "-f", "--", *(p.as_posix() for p in new_files), cwd=out)

    tree = git("write-tree", cwd=out)
    if tree != RESULT_TREE:
        sys.exit(f"Assembled tree {tree} does not match the expected {RESULT_TREE}")
    git(*IDENTITY, "commit", "--quiet", "-m", "Apply the hackathon work (assemble.py)", cwd=out)
    print(f"Assembled FORGE-0 in {out}: {len(patches)} patches, {len(new_files)} new files.")
    print("Tree matches the benchmarked version. Next: see README.md and docs/OPERATIONS.md there.")


if __name__ == "__main__":
    main()
