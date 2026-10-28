# FORGE-0: hackathon work

**FORGE-0 is an evidence-driven debugging agent.** Given a failing test, it forms competing
root-cause hypotheses, runs experiments in an isolated sandbox to tell them apart, and proposes a
patch only once the evidence points to a cause. An independent verifier must then accept the patch.
The point is that a fix claim comes with proof, so a reviewer doesn't have to trust the agent.

This repository holds **only the work done during the Meta Global AI Developer Hackathon**
(Indie Developer track, *Push the Frontier*), from kickoff on Oct 26, 2026 onward.

## What was pre-existing and what is new

| | Where | When |
| --- | --- | --- |
| **Pre-existing** core: the seven-agent pipeline, sandbox, verifier, dashboard, mock provider, a Meta provider written to the documented contract but never run, defects D1–D5 and a one-shot benchmark | [forge-0-core](https://github.com/waleedmustafa971/forge-0-core), a separate repository, labelled there | Up to Oct 19, 2026 |
| **Built during the hackathon** (listed below) | This repository: [`new/`](new) holds files created during the event, [`patches/`](patches) holds changes to pre-existing files | Oct 26 – Nov 4, 2026 |

[NEW_WORK.md](NEW_WORK.md) lists every new file, and for every pre-existing file the exact line
ranges changed during the hackathon. The core is a dependency here, the same way a library would be:
no pre-existing file is copied into this repository. (Like any diff, the patches carry a few lines of
surrounding pre-existing code as context, and the lines they remove.) This repository's own files,
`assemble.py`, `.devcontainer/` and its workflow, were also written during the event.

## Built during the hackathon

1. **First real-model runs on Meta Muse Spark 1.3**, and the fixes they forced: replies cut off at
   `max_completion_tokens` are retried with a higher limit, and a probe the runtime fails
   (`unhandledRejection`) no longer counts as evidence against a correct prediction.
2. **A fair baseline.** Besides the one-shot baseline, an edit → run tests → retry loop with the same
   call budget as FORGE-0, the way coding agents work today. The benchmark compares all three.
3. **Harder defects.** D6–D9, each designed to defeat a one-shot fix (two causes, a contract tested
   in another file, a stateful regex, an order-dependent test), plus D10–D12, pre-registered
   before they were run.
4. **A real open-source bug.** R1: [`parse`](https://github.com/r1chardj0n3s/parse) issue #162,
   vendored at the commit before the upstream fix (third-party code, MIT, under
   `new/demo/real-world/parse/`), with the project's own regression test. This also made the
   **pytest** runner real.
5. **Flaky-test triage.** Re-runs classify each failure as deterministic, intermittent or
   order-dependent before any hypothesis is formed. The verifier adapts its re-runs to the class.
6. **GitHub integration.** On a CI failure in one of the repository's own branches, or on a
   `forge0`-labelled issue, a GitHub Action runs
   FORGE-0 and opens a pull request whose description is the evidence. When no fix survives
   verification, it posts the evidence as an issue comment instead.
7. **Two Meta models in two roles.** Muse Spark 1.3 forms the hypotheses; the open-weights Muse
   Spark Open designs experiments and writes repairs. Each call records which model served it.
8. **Smarter context selection.** Relevant files are ranked (stack trace → the files it names →
   their imports), so a root cause two imports away isn't dropped by the file cap.

## Results (all from the hackathon)

* **Muse Spark 1.3, 10 defects × 3 repeats:** FORGE-0 fixed 30/30, confirmed by hidden tests, with
  no false fix claims. The one-shot baseline made 2 false claims.
* **FORGE-0 doesn't beat the edit-test loop on fix rate.** They tie on Muse Spark 1.3, including on
  the pre-registered D10–D12. On Muse Spark Open alone, the loop fixed 38/39 and FORGE-0 30/39.
  FORGE-0's advantage is precision and the evidence behind each fix: across the three benchmarks of
  the current code, 78 FORGE-0 runs made no false fix claims, against 2 in 39 for the one-shot
  baseline and 1 in 78 for the loop.

Full results, including the losses, are in `docs/EVALUATION.md` and
`benchmarks/preregistration/2026-10-27-harder-defects.md` (in [`patches/`](patches) and [`new/`](new)).

## See it work, with nothing to install

**Real Muse Spark runs on GitHub.** In [forge-0-demo](https://github.com/waleedmustafa971/forge-0-demo),
labelling an issue `forge0` starts FORGE-0 in GitHub Actions on Muse Spark 1.3. Its issues and pull
requests show the results: the PR description is the evidence (the explanations FORGE-0 considered,
the experiments that ruled some out, and the independent verification), and CI checks the fix by
test name: the target test now passes, and every test that passed before still passes.

**Try it in your browser.**
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/waleedmustafa971/forge-0-hackathon)
The codespace assembles and installs FORGE-0. The first start takes several minutes, and its
creation log stays on screen until FORGE-0 answers; then the dashboard opens on port 8010 (if your
browser blocks the new tab, open it from the *Ports* panel).
[![Codespace smoke test](https://github.com/waleedmustafa971/forge-0-hackathon/actions/workflows/codespace.yml/badge.svg)](https://github.com/waleedmustafa971/forge-0-hackathon/actions/workflows/codespace.yml)
checks this on every change: it builds the same dev container and runs the investigation below. Without a key, FORGE-0 runs on its clearly labelled mock provider (scripted
model replies for D1–D5), while the sandbox, experiments and verification are real. Choose
*Start investigation* → *Scan tests* → "charges the customer exactly once when a timed-out request
is retried" to watch FORGE-0 reject a patch that breaks another test, then verify a revised one. To
run on Muse Spark 1.3, save a Meta Model API key as a Codespaces secret named `META_API_KEY`. The
*Evaluation* page shows every real-model benchmark run.

## Run it locally

Requirements: Python 3.12+, Git, Node.js 22.18+, and Docker.

```bash
git clone https://github.com/waleedmustafa971/forge-0-hackathon.git
cd forge-0-hackathon
python assemble.py     # clones the core, applies this repository's work, verifies it, writes ./forge-0
cd forge-0
./scripts/dev.sh       # Linux/macOS: API on :8010, dashboard on :5173
.\scripts\lite.ps1 start   # Windows instead: API and dashboard on http://127.0.0.1:8010
```

`assemble.py` checks out the pre-hackathon core, applies the patches, adds the new files, and checks
that the result is byte for byte the development repository's current version. Since the benchmarks ran, FORGE-0's
code has had two bug fixes, found while recording the demo on PostgreSQL: a repair's hypothesis key
is stored as `H1` instead of the model's longer text (which failed the database insert), and the
dashboard's reproduction badge shows the flaky-test triage result. Neither changes what FORGE-0
decides. Everything else since then is documentation and the GitHub workflow template. FORGE-0 runs on its clearly
labelled mock provider unless you set `AI_PROVIDER=meta` and `META_API_KEY` in `forge-0/.env` (or
choose the provider in *Settings*), which runs it on Muse Spark 1.3.

## License

MIT, see [LICENSE](LICENSE). The vendored `parse` library keeps its own MIT license.
