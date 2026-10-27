# Pre-registration: harder defects and an open-weights arm (2026-10-27)

Written and committed **before** any of the runs below. The git history of this file is the
evidence that the defects, predictions and decision rules were fixed in advance.

## Why

In run `20261027-101729-meta` (Muse Spark 1.3, 10 defects × 3 repeats), Baseline C (edit → run
tests → retry) and FORGE-0 both fixed 30/30. The defects did not separate them. The question is
whether that is because the method adds nothing to fix rate, or because the defects were readable:
in every one of them the root cause could be found by reading the code in the prompt.

Both systems get the same context (the same relevant files). The only thing FORGE-0 can do that
Baseline C cannot is **observe the running program**: probe tests and counterfactual edits whose
output it reads. A defect separates the two only if

1. the root cause is a *runtime* fact (a value, an identity, an ordering) that is hard to infer from
   the code in the prompt, and
2. a plausible local patch makes every visible test pass while leaving the root cause in place, so
   the loop has no test feedback telling it to keep going.

## New defects (D10–D12)

| Id | Root cause (runtime fact) | Local patch that passes every visible test (the trap) | Hidden tests catch it because |
| --- | --- | --- | --- |
| D10-string-config | `config/fees.json` stores fees as strings (`"2.50"`); it is read at runtime with `readFileSync`, so it is never in the prompt. `merchandise + fee` concatenates and the quote is `NaN` | `Number(fees.handlingFee)` at the failing call site, or coercing only `handlingFee` in the loader | the gift-wrap fee has the same problem on a path no visible test covers |
| D11-closure-dedupe | checkout attaches its `order.paid` subscribers on every call through `onUnique`, which dedupes by function identity; each call passes a fresh arrow function, so subscribers pile up | de-duplicating loyalty awards by order id | receipts are duplicated the same way, and the listener count grows without bound |
| D12-integer-keys | cart lines are stored in a plain object keyed by numeric product id; JavaScript orders integer-like keys numerically, not by insertion | storing an insertion sequence and sorting in `lines()` | checkout builds order items from the same object without going through `lines()` |

Each defect gets a failing test, regression tests that pass before the fix, a reference fix,
hidden tests, and checked traps (the trap patch must pass every visible test and fail a hidden
test), like D6–D9.

## Predictions (made before running)

| Defect | Baseline C (loop) | FORGE-0 | Reasoning |
| --- | --- | --- | --- |
| D10 | fails often | fixes more often | the `NaN` gives no hint that *every* fee is a string; a probe that prints `typeof` the loaded fees does |
| D11 | fails sometimes | fixes more often | "points doubled" invites a dedupe in loyalty; counting listeners shows the leak |
| D12 | fixes | fixes | integer-key ordering is well known; expected to be a tie |

## Arms

* **A. Muse Spark 1.3**: D10–D12 × Baseline A / Baseline C / FORGE-0 × 3 repeats, the same
  settings as `muse-spark-1.3.json`.
* **B. Open weights only**: Muse Spark Open (`meta-models/muse-spark-open-1026` on Baseten) as the
  single model for every task; all 13 defects (D1–D12, R1) × Baseline C / FORGE-0 × 3 repeats.
  Hypothesis: the structure matters more for a model that is weaker at reading code, so the gap is
  larger than with Muse Spark 1.3.

## Decision rules

* Every pre-registered defect and arm is reported, whatever the outcome. None is dropped or
  re-tuned after its results are seen.
* "FORGE-0 beats the loop on fix rate" is claimed only for an arm where FORGE-0's total of
  hidden-test-confirmed fixes is higher than Baseline C's, and is reported together with the
  per-defect counts and the cost.
* If FORGE-0 itself is changed after these runs, the change is re-run on **all** defects and
  reported as a new run, not merged into these numbers.
* A defect found to be broken (e.g. a reference fix that fails its hidden tests) is fixed and the
  whole arm re-run; the broken run is reported too.

## Results (added after the runs, 2026-10-27)

Everything above this heading is unchanged from commit `3c554f4`. Both arms ran as specified; no
defect was dropped or re-tuned, and FORGE-0 was not changed between them.

**Arm A: Muse Spark 1.3, D10–D12 × 3 repeats.** Run `20261027-115421-meta`, $1.02.

| Defect | Baseline A · one-shot | Baseline C · loop | FORGE-0 |
| --- | --- | --- | --- |
| D10-string-config | 3/3 | 3/3 | 3/3 |
| D11-closure-dedupe | 3/3 | 3/3 (one run needed a second attempt) | 3/3 |
| D12-integer-keys | 3/3 | 3/3 | 3/3 |
| Total · false claims · cost per run | 9/9 · 0 · $0.019 | 9/9 · 0 · $0.020 | 9/9 · 0 · $0.075 |

The predictions for D10 and D11 were **wrong**: every system, including the one-shot baseline,
found the runtime fact from the code and the failing assertion, and fixed the whole cause (every
fee, the subscription itself) rather than the local symptom. D12 tied, as predicted.

**Arm B: Muse Spark Open only, D1–D12 + R1 × 3 repeats.** Run `20261027-132544-openai`, $6.06.

| | Baseline C · loop | FORGE-0 |
| --- | --- | --- |
| Fixed (hidden-test confirmed) | **38/39** | 30/39 |
| False fix claims | 1 (D1 #1: passed the visible tests, failed the hidden ones) | **0** |
| Runs lost to a failed model call | 0 | 7 (D1 ×2, D2, D3, D5, D12 ×2) |
| Inconclusive | 0 | 2 (D11 #1, #3) |
| Model calls · cost per run | 40 · $0.020 | 120 · $0.135 |

All seven of FORGE-0's lost runs failed in the same place: the experiment-design call, where Muse
Spark Open spent the whole 16,384-token completion budget on reasoning and returned no usable plan
(six empty, one truncated). The loop never makes that call. On the 32 runs where every call
returned, FORGE-0 fixed 30. The hypothesis that the structure helps a weaker code reader more was
**not supported**: the loop did better.

**Decision.** Under the rule above, FORGE-0 does **not** beat the loop on fix rate in either arm
(A: 9 vs 9; B: 30 vs 38). In arm B it made no false claims where the loop made one. Fixing the
experiment-design failure on open models is a change to FORGE-0, so its effect has to be measured
as a new run on all defects, not merged into these numbers.
