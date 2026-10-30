# FORGE-0: hackathon work

**FORGE-0 is an evidence-driven debugging agent.** Given a failing test, it forms competing
root-cause hypotheses, runs experiments in an isolated sandbox to tell them apart, and proposes a
patch only once the evidence points to a cause. An independent verifier must then accept the patch.
The point is that a fix claim comes with proof, so a reviewer doesn't have to trust the agent.

This repository holds **only the work done during the Meta Global AI Developer Hackathon**
(Indie Developer track, *Push the Frontier*), from kickoff on Oct 26, 2026 onward.

## The problem

AI coding assistants are now fast at writing fixes, but a fix that *looks* right isn't the same as one
that *is* right. When a test fails, an assistant usually takes the first plausible explanation and
writes a patch. If that explanation is wrong, the patch can still make the test pass and break
something else, or fix a symptom while the cause stays. The work then moves to the reviewer, who has
to re-debug the problem to know whether to trust the patch. For a team that ships to production, an
AI fix nobody can check is a risk, not a saving.

## Why FORGE-0 stands out

* **It checks before it claims.** Muse Spark proposes several competing explanations, and each one
  commits in advance to what an experiment should show if it is true. FORGE-0 runs those
  experiments and keeps only the explanation the evidence supports. The model's reasoning is tested,
  not trusted.
* **Every fix comes with its proof.** The pull request description is the evidence: the root cause,
  the explanations considered, the experiments that ruled some out, and the independent
  verification. A reviewer reads the evidence instead of re-debugging.
* **It says "I don't know" instead of guessing.** When no fix survives verification, FORGE-0 opens
  no pull request. It posts the evidence as an issue comment instead, including the patches the
  verifier rejected and why.
* **Its claims are measured, including where it loses.** Hidden tests that FORGE-0 never sees score
  every run, the harder defects were pre-registered before they ran, and the results below report
  the losses too.

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

## Shipping safely: CI/CD with AI in the loop

FORGE-0 sits inside the delivery pipeline teams already use, so AI help doesn't bypass the checks
they already trust:

1. **The pipeline is the trigger.** A CI failure on one of the repository's own branches, or an
   issue labelled `forge0`, starts FORGE-0 in GitHub Actions. Nobody has to paste code into a chat.
2. **Untrusted code runs in a locked-down sandbox.** Experiments and tests run in Docker with no
   network, a read-only root filesystem, a non-root user with all capabilities dropped, resource
   limits and a hard timeout, and only allowlisted test runners; the model never writes shell
   commands.
3. **A fix has to pass twice.** FORGE-0's independent verifier re-runs the whole suite on a fresh
   copy, and then the repository's own CI checks the pull request test by test: the target test now
   passes, and every test that passed before still passes.
4. **A human still merges.** FORGE-0 opens a pull request; it never merges. Developers keep the
   decision, with the evidence in front of them.
5. **Cost is bounded and visible.** Each investigation has budgets for model calls, experiments,
   repair attempts and time, and reports its token use and cost. The live runs cost $0.07–$0.12
   each.

For developers, a red build arrives with a candidate fix and the reasons to believe it. For a
company, that means AI speed without lowering the bar for what reaches the main branch: no
unverified patch, no silent regression, and a record of why each change was made.

## How Meta's Muse models shaped FORGE-0

Before the hackathon, FORGE-0 had never run on a real model. The hackathon work grew out of running
it on Muse Spark:

* **Muse Spark 1.3 is the reasoning engine.** Its JSON-schema structured outputs make each
  hypothesis, prior, prediction and experiment plan machine-checkable, which is what lets FORGE-0
  hold the model to its own predictions. `reasoning_effort` is the cost/quality dial, and the usage
  accounting (including reasoning and cached tokens) feeds each investigation's cost report.
* **The first real runs forced real fixes.** Replies cut off when reasoning used the whole
  `max_completion_tokens` budget are now detected and retried with a higher limit, and a probe the
  runtime itself fails no longer counts as evidence against a correct prediction.
* **Muse Spark Open (open weights, on Baseten) made model routing possible.** Muse Spark 1.3 forms
  the hypotheses, and Muse Spark Open designs experiments and writes repairs; each call records which
  model served it. A team that can't send private code to a closed model can run the same verified
  workflow on open weights.
* **Muse Spark Open also exposed FORGE-0's weakest point.** In 7 of 39 runs, experiment design
  returned no plan because the model spent its whole token budget reasoning. That result is
  reported, not hidden, and it is the next thing to fix.
* **Muse Voice Transcribe** timed the captions of the demo video.

## For the judges

| Criterion | Where to check it |
| --- | --- |
| **Impact**: a real problem for real teams | Unverified AI fixes are a review and production risk. FORGE-0 works where teams already work (GitHub Actions and pull requests), made no false fix claims in 78 benchmark runs, and was tested on a real upstream bug (R1, `parse` #162). |
| **Use of Meta AI tooling** | Muse Spark 1.3 on the Meta Model API (structured outputs, reasoning effort, usage accounting), Muse Spark Open on Baseten in a two-model route, and Muse Voice Transcribe for the video. Muse Spark 1.3 wrote the three public pull requests in [forge-0-demo](https://github.com/waleedmustafa971/forge-0-demo), running in GitHub Actions. |
| **Technical depth** | Competing hypotheses with pre-committed predictions, experiments in an isolated sandbox, belief updates, an independent verifier, flaky-test triage, ranked context selection, a fair edit-test baseline, hidden-test scoring and pre-registered defects. |
| **Demo** | The [3-minute video](https://youtu.be/DmIuamMJUTg), the live PRs in forge-0-demo, and a one-click Codespace whose smoke test runs on every change. |
| **New work only** | The pre-existing core is in [forge-0-core](https://github.com/waleedmustafa971/forge-0-core); [NEW_WORK.md](NEW_WORK.md) lists every file and line range written during the event. |

### Final check before submission (Oct 30, 2026)

| Check | Result |
| --- | --- |
| Fresh clone of this repository, then `python assemble.py` | 53 patches and 90 new files applied; the tree is byte for byte identical to the development repository |
| Backend unit and API tests | 132 passed |
| Sandbox integration tests on real Docker | 17 passed |
| Frontend tests | 13 passed |
| Double-charge demo audit (`scripts/audit_demo.py`, mock provider) | 17/17 checks passed |
| Live investigation of the same bug on Muse Spark 1.3 | Verified fix in 87 s: 3 experiments, 11 sandbox runs, $0.077, no failed model calls |
| Meta Model API connectivity and a live completion | OK |
| CI on the public repositories (Codespace smoke test, demo contract, core) | Passing |

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
