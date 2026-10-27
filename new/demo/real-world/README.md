# Real-world bugs (evaluation material)

Planted defects show the mechanism; these cases show FORGE-0 on bugs that shipped in real
open-source projects. Each case vendors the project **at the commit just before the upstream fix**,
plus the regression test that the fix added, so the failing test is the project's own and the
reference fix is the patch the maintainers merged. Case descriptions and reference fixes live in
`cases/` (outside the vendored repository, so investigation agents never see them).

| Case | Project | Upstream | Bug |
| --- | --- | --- | --- |
| [R1-parse-microseconds](cases/R1-parse-microseconds/defect.json) | [`parse`](https://github.com/r1chardj0n3s/parse) (MIT) | issue #162, fix `ba6803d` | timestamps lose microseconds to float truncation (`08.501902` → 501901 µs) |

`parse/` is vendored from upstream commit `738447715c76` (MIT license, see `parse/LICENSE`) with
`tests/test_bugs.py` taken from the fix commit `ba6803d57179`. Nothing else was changed.

Run it like any benchmark defect:

```bash
backend/.venv/Scripts/python benchmarks/run_benchmark.py --config benchmarks/configs/muse-spark-1.3.json \
  --defects R1-parse-microseconds --dry-run
```

Python cases need the sandbox image `forge0/sandbox-python:3.12` (`scripts/build_sandbox_images.sh`).

These cases were added during the Meta hackathon (2026-10-27).
