"""Assemble a runnable FORGE-0: the pre-hackathon core plus the hackathon work in this repository.

    python assemble.py                     # clones the core from GitHub into ./forge-0
    python assemble.py --core PATH --out DIR

Steps: clone the core, check out the commit whose tree is the Oct 19 core, apply every patch in
patches/ (changes to pre-existing files), copy new/ (files created during the hackathon) on top,
and check that the result is byte-for-byte the expected tree. The work happens in a temporary
directory next to the output, which is renamed only once the check passes: the output directory
either holds a verified FORGE-0 or does not exist.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

CORE_URL = "https://github.com/waleedmustafa971/forge-0-core.git"
CORE_TREE = "2b92b06020c31a745a6a63678b335eaf0651bf94"  # git tree of the pre-hackathon core (Oct 19, 2026)
RESULT_TREE = "976de4fbbafcf7b161f3369b24c3a483bef0d8ae"  # git tree of core + hackathon work
HERE = Path(__file__).resolve().parent
# A fixed identity, no signing and no hooks, so the judge's git configuration cannot get in the way.
COMMIT_CONFIG = [
    "-c", "user.name=assemble.py", "-c", "user.email=assemble@localhost",
    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=no-hooks",
]


def git(*args, cwd=None):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        command = " ".join(a for a in args if not a.startswith("-"))[:80]
        sys.exit(f"git {command} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--core", default=CORE_URL, help="core repository URL or path")
    parser.add_argument("--out", default="forge-0", help="directory to create")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    work = out.with_name(f".{out.name}.partial")
    if out.exists():
        sys.exit(f"{out} already exists")
    if work.exists():
        sys.exit(f"{work} is left over from an interrupted run; delete it and run again")

    git("clone", "--quiet", "-c", "core.autocrlf=false", "-c", "core.longpaths=true",
        args.core, str(work))
    commits = git("rev-list", "--all", cwd=work).split()
    base = next((c for c in commits if git("rev-parse", f"{c}^{{tree}}", cwd=work) == CORE_TREE), None)
    if base is None:
        sys.exit("No commit in the core repository has the expected pre-hackathon tree")
    git("checkout", "--quiet", "-b", "assembled", base, cwd=work)

    # Apply to the index, then write it out, so local line-ending settings cannot reject a patch.
    patches = sorted(str(p) for p in (HERE / "patches").rglob("*.patch"))
    git("apply", "--cached", *patches, cwd=work)
    git("checkout", "--", ".", cwd=work)

    new_files = sorted(p.relative_to(HERE / "new") for p in (HERE / "new").rglob("*") if p.is_file())
    shutil.copytree(HERE / "new", work, dirs_exist_ok=True)
    git("add", "-f", "--", *(p.as_posix() for p in new_files), cwd=work)

    tree = git("write-tree", cwd=work)
    if tree != RESULT_TREE:
        sys.exit(f"Assembled tree {tree} does not match the expected {RESULT_TREE}; see {work}")
    git(*COMMIT_CONFIG, "commit", "--quiet", "-m", "Apply the hackathon work (assemble.py)", cwd=work)
    work.rename(out)
    print(f"Assembled FORGE-0 in {out}: {len(patches)} patches, {len(new_files)} new files.")
    print("Tree verified. Next: see 'Run it locally' in this repository's README.")


if __name__ == "__main__":
    main()
