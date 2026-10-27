# FORGE-0 for GitHub

Turns FORGE-0 from a dashboard into part of the workflow: when CI fails, or when someone labels an
issue `forge0`, FORGE-0 investigates in its sandbox and either

* **opens a pull request** with the verified patch, whose description is the evidence report
  (the explanations it considered, the experiments it ran, which explanations the evidence ruled
  out, and the independent verification), or
* **comments on the issue** with what it learned and why it did not propose a fix, when no patch
  survives verification. It never opens a PR for an unverified patch.

A human always reviews and merges. Added during the Meta hackathon (2026-10-27).

**Verified on GitHub Actions (2026-10-27):** issue
[#1](https://github.com/waleedmustafa971/forge-0/issues/1) in this repository, labelled `forge0`,
triggered [`forge0-selftest.yml`](../../.github/workflows/forge0-selftest.yml) (the same steps,
pointed at `demo/order-management`). FORGE-0 reproduced the D6 refund defect, ran four experiments
that refuted two of its three explanations, and opened
[PR #2](https://github.com/waleedmustafa971/forge-0/pull/2) as `forge0[bot]` with a verified fix
for both causes, the evidence as its description and `Closes #1`. About $0.07 of Muse Spark 1.3.
The PR was closed unmerged because the defect is a benchmark fixture.

A later run (issue #8 → PR #9, D5) also exercised the CI hand-off: the workflow dispatched CI on
the fix branch, and its checks passed on the PR's commit (the demo contract: exactly one defect
fixed, 32 passing / 11 failing, no regressions). Not every run ends in a PR: on issue #5 FORGE-0
ended D6 inconclusive and commented its evidence on the issue instead.

## Setup

1. Copy [`forge0.yml`](forge0.yml) to `.github/workflows/forge0.yml` in the repository to protect.
2. Set `workflows: ["CI"]` (and `CI_WORKFLOW`) to the name of the workflow whose failures should
   trigger FORGE-0, and give that workflow a `workflow_dispatch:` trigger.
3. Add the repository secret `META_API_KEY` (Meta Model API). If your copy of FORGE-0 is a private
   repository, also add a read-only deploy key for it as `FORGE0_DEPLOY_KEY`. Optionally add
   `OPENAI_COMPAT_API_KEY` (e.g. a Baseten key) and set `AI_SECONDARY_PROVIDER: openai` to run
   experiment design and repairs on Muse Spark Open while Muse Spark 1.3 forms the hypotheses.
4. Allow Actions to create pull requests: *Settings → Actions → General → Workflow permissions →
   Allow GitHub Actions to create and approve pull requests*.

To trigger it from an issue, add the `forge0` label. Name the test in the issue body with a line
like `Failing test: does not allow a cancelled order to be paid or shipped`; without one, FORGE-0
investigates the first failing test.

## What runs

The workflow checks out the failing commit (or the default branch for issues), installs FORGE-0,
and runs `forge0-ci`:

```bash
forge0-ci --repo . --open-pr --base main                    # after a failed CI run
forge0-ci --repo . --issue-body-file issue.md --comment-issue 42 --open-pr --base main
forge0-ci --repo . --dry-run                                # print the git/gh commands instead
```

The full evidence report (`forge0-report.md` and `.json`) is uploaded as a workflow artifact, and
the PR description (or comment) is added to the job summary.

## Limits

* The sandbox is offline and does not install dependencies: the project's tests must run with
  Node's built-in runner (`node --test`, TypeScript via type stripping) or with pytest and the
  standard library. Projects that need `npm install` / `pip install` are not supported yet.
* Pull requests created with the workflow's `GITHUB_TOKEN` do not trigger `pull_request`
  workflows (GitHub shows a failed run with no jobs). The workflow therefore dispatches
  `CI_WORKFLOW` on the fix branch, so that workflow needs a `workflow_dispatch:` trigger; its
  checks then appear on the PR.
* Each run spends model tokens: a typical investigation costs a few cents at Muse Spark 1.3 list
  prices; the per-investigation budget (`MAX_MODEL_CALLS`, `MAX_EXPERIMENTS`) bounds it.
