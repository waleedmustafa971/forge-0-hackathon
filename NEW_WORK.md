# Provenance: what was written during the hackathon

The pre-hackathon core is commit `0d3dde1` of the development repository (Oct 19, 2026), published
unchanged as [forge-0-core](https://github.com/waleedmustafa971/forge-0-core) (tag
`pre-hackathon-2026-10-19`). Nothing was written between that commit and the hackathon kickoff on
Oct 26, 2026. Everything below was written after kickoff.

This file is generated from `git diff 0d3dde1 HEAD` of the development repository.

## 88 files created during the hackathon (in `new/`)

`new/demo/real-world/parse/` is third-party code: the open-source
[`parse`](https://github.com/r1chardj0n3s/parse) library (MIT), vendored as a test subject (R1).
Its tests and code aren't FORGE-0 work.

| File | Lines |
| --- | --- |
| `.github/workflows/forge0-selftest.yml` | 83 |
| `backend/cli/__init__.py` | 0 |
| `backend/cli/ci.py` | 253 |
| `backend/providers/routing.py` | 47 |
| `backend/sandbox/images/python/forge0_pytest.py` | 24 |
| `backend/sandbox/junit.py` | 83 |
| `backend/services/pr_report.py` | 148 |
| `backend/tests/test_ci.py` | 103 |
| `backend/tests/test_executor_classify.py` | 37 |
| `backend/tests/test_flakiness.py` | 28 |
| `backend/tests/test_junit.py` | 36 |
| `backend/tests/test_relevant_files.py` | 56 |
| `backend/tests/test_routing.py` | 73 |
| `benchmarks/configs/harder-muse-spark-1.3.json` | 32 |
| `benchmarks/configs/muse-spark-two-models.json` | 26 |
| `benchmarks/configs/open-weights-muse-spark-open.json` | 25 |
| `benchmarks/hidden-tests/D10-string-config.test.ts` | 22 |
| `benchmarks/hidden-tests/D11-closure-dedupe.test.ts` | 39 |
| `benchmarks/hidden-tests/D12-integer-keys.test.ts` | 30 |
| `benchmarks/hidden-tests/D6-layered-refund.test.ts` | 44 |
| `benchmarks/hidden-tests/D7-stale-price-cache.test.ts` | 33 |
| `benchmarks/hidden-tests/D8-stateful-regex.test.ts` | 29 |
| `benchmarks/hidden-tests/D9-order-dependent-cache.test.ts` | 26 |
| `benchmarks/hidden-tests/test_R1_parse_microseconds.py` | 20 |
| `benchmarks/preregistration/2026-10-27-harder-defects.md` | 100 |
| `benchmarks/results/20261027-072844-meta.html` | 35 |
| `benchmarks/results/20261027-072844-meta.json` | 1414 |
| `benchmarks/results/20261027-101729-meta.html` | 35 |
| `benchmarks/results/20261027-101729-meta.json` | 3969 |
| `benchmarks/results/20261027-103750-meta+openai.html` | 35 |
| `benchmarks/results/20261027-103750-meta+openai.json` | 214 |
| `benchmarks/results/20261027-115421-meta.html` | 35 |
| `benchmarks/results/20261027-115421-meta.json` | 1439 |
| `benchmarks/results/20261027-132544-openai.html` | 35 |
| `benchmarks/results/20261027-132544-openai.json` | 3975 |
| `demo/defects/D10-string-config/defect.json` | 27 |
| `demo/defects/D10-string-config/reference-fix.json` | 11 |
| `demo/defects/D11-closure-dedupe/defect.json` | 27 |
| `demo/defects/D11-closure-dedupe/reference-fix.json` | 16 |
| `demo/defects/D12-integer-keys/defect.json` | 26 |
| `demo/defects/D12-integer-keys/reference-fix.json` | 31 |
| `demo/defects/D6-layered-refund/defect.json` | 28 |
| `demo/defects/D6-layered-refund/reference-fix.json` | 11 |
| `demo/defects/D7-stale-price-cache/defect.json` | 30 |
| `demo/defects/D7-stale-price-cache/reference-fix.json` | 26 |
| `demo/defects/D8-stateful-regex/defect.json` | 27 |
| `demo/defects/D8-stateful-regex/reference-fix.json` | 11 |
| `demo/defects/D9-order-dependent-cache/defect.json` | 25 |
| `demo/defects/D9-order-dependent-cache/reference-fix.json` | 26 |
| `demo/order-management/config/fees.json` | 5 |
| `demo/order-management/src/config/fees.ts` | 16 |
| `demo/order-management/src/domain/giftCardCode.ts` | 10 |
| `demo/order-management/src/gateways/cachingPricing.ts` | 22 |
| `demo/order-management/src/gateways/priceBook.ts` | 26 |
| `demo/order-management/src/lib/events.ts` | 29 |
| `demo/order-management/src/services/cartService.ts` | 53 |
| `demo/order-management/src/services/catalogService.ts` | 26 |
| `demo/order-management/src/services/checkoutService.ts` | 65 |
| `demo/order-management/src/services/giftCardService.ts` | 58 |
| `demo/order-management/src/services/loyaltyService.ts` | 35 |
| `demo/order-management/src/services/quoteService.ts` | 39 |
| `demo/order-management/src/services/refundService.ts` | 32 |
| `demo/order-management/test/cart.test.ts` | 35 |
| `demo/order-management/test/catalog.test.ts` | 25 |
| `demo/order-management/test/checkout-events.test.ts` | 35 |
| `demo/order-management/test/giftCards.test.ts` | 24 |
| `demo/order-management/test/loyalty.test.ts` | 24 |
| `demo/order-management/test/pricing-cache.test.ts` | 20 |
| `demo/order-management/test/quotes.test.ts` | 25 |
| `demo/order-management/test/refunds.test.ts` | 47 |
| `demo/real-world/README.md` | 25 |
| `demo/real-world/cases/R1-parse-microseconds/defect.json` | 32 |
| `demo/real-world/cases/R1-parse-microseconds/reference-fix.json` | 11 |
| `demo/real-world/parse/.pytest.ini` | 2 |
| `demo/real-world/parse/LICENSE` | 19 |
| `demo/real-world/parse/README.rst` | 530 |
| `demo/real-world/parse/parse.py` | 1090 |
| `demo/real-world/parse/pyproject.toml` | 38 |
| `demo/real-world/parse/tests/requirements.txt` | 2 |
| `demo/real-world/parse/tests/test_bugs.py` | 121 |
| `demo/real-world/parse/tests/test_findall.py` | 26 |
| `demo/real-world/parse/tests/test_parse.py` | 793 |
| `demo/real-world/parse/tests/test_parsetype.py` | 216 |
| `demo/real-world/parse/tests/test_pattern.py` | 96 |
| `demo/real-world/parse/tests/test_result.py` | 38 |
| `demo/real-world/parse/tests/test_search.py` | 24 |
| `integrations/github/README.md` | 68 |
| `integrations/github/forge0.yml` | 130 |

## 53 pre-existing files changed during the hackathon (in `patches/`)

Line ranges refer to the file after the change. Every other line in these files is pre-existing.

| File | Lines added / removed | Lines added or changed |
| --- | --- | --- |
| `.env.example` | +6 / -0 | 50-55 |
| `.github/workflows/ci.yml` | +10 / -2 | 38-40, 113-116, 122-124 |
| `.gitignore` | +1 / -0 | 13 |
| `CONTRIBUTING.md` | +1 / -1 | 24 |
| `README.md` | +106 / -32 | 9-14, 16-18, 48-54, 60-86, 131, 139-169, 173-174, 177, 179-182, 184-187, 197-202, 217, 219-224, 229-230, 244-245, 252, 254-255 |
| `backend/agents/belief.py` | +22 / -5 | 12-14, 89-91, 94-104, 128-131, 139 |
| `backend/agents/executor.py` | +24 / -2 | 21-23, 34-43, 61-69, 81-82 |
| `backend/agents/investigator.py` | +73 / -12 | 4-6, 17, 26-28, 68-107, 205-222, 226-233 |
| `backend/agents/orchestrator.py` | +66 / -9 | 50-56, 119, 163, 168-170, 178-181, 312, 321, 347, 560-604, 665-666 |
| `backend/agents/prompts.py` | +33 / -4 | 30-35, 39-44, 70-72, 178-195 |
| `backend/agents/repair.py` | +19 / -1 | 8, 56-73 |
| `backend/agents/verifier.py` | +10 / -5 | 5-6, 19-20, 138-141, 143, 145 |
| `backend/api/routes/system.py` | +4 / -2 | 182-184, 186 |
| `backend/api/schemas.py` | +1 / -1 | 47 |
| `backend/core/config.py` | +5 / -0 | 59-63 |
| `backend/core/models.py` | +1 / -1 | 53 |
| `backend/core/schemas.py` | +10 / -0 | 94-102, 117 |
| `backend/providers/mock.py` | +4 / -1 | 58, 107-109 |
| `backend/providers/openai_compat.py` | +41 / -11 | 95-97, 196-203, 219-221, 223, 233, 244, 250-263, 265, 287-288, 291, 300-302, 304-305, 307 |
| `backend/providers/registry.py` | +24 / -1 | 13, 28-47, 64-66 |
| `backend/pyproject.toml` | +4 / -1 | 28-30, 32 |
| `backend/sandbox/docker.py` | +3 / -1 | 32, 272-273 |
| `backend/sandbox/images/python/Dockerfile` | +2 / -0 | 6-7 |
| `backend/sandbox/runners.py` | +21 / -2 | 72-91, 93 |
| `backend/services/repo_analysis.py` | +87 / -6 | 8-9, 74-90, 214-232, 246-259, 263-272, 281-294, 299, 311-320 |
| `backend/services/reports.py` | +7 / -3 | 179-183, 202, 227 |
| `backend/tests/conftest.py` | +2 / -0 | 20-21 |
| `backend/tests/fakes.py` | +5 / -2 | 79-81, 84, 117 |
| `backend/tests/test_api.py` | +20 / -0 | 223-242 |
| `backend/tests/test_belief.py` | +26 / -0 | 49-74 |
| `backend/tests/test_benchmark_config.py` | +8 / -5 | 27, 50-55, 57 |
| `backend/tests/test_integration_docker.py` | +7 / -4 | 19-21, 55-56, 86, 98 |
| `backend/tests/test_meta_contract.py` | +22 / -7 | 196-197, 200, 203-221 |
| `backend/tests/test_orchestrator.py` | +31 / -0 | 140-170 |
| `benchmarks/configs/muse-spark-1.3.json` | +4 / -3 | 3, 10, 14-15 |
| `benchmarks/run_benchmark.py` | +82 / -27 | 50, 54-58, 61-64, 73-74, 105-109, 130, 157-159, 163-164, 175-177, 191-192, 206-207, 269-270, 272-275, 280-281, 285, 293-299, 316, 334-337, 339-340, 342-343, 354-355, 361, 384, 390-393, 417, 444-449, 509-510, 541-544, 549-554 |
| `demo/defects/README.md` | +33 / -2 | 14-44, 50, 54 |
| `demo/order-management/src/app.ts` | +27 / -1 | 1, 5-6, 8, 11-13, 15-16, 19-20, 37-41, 49, 51, 53-61 |
| `demo/order-management/src/domain/types.ts` | +13 / -0 | 32-43, 63 |
| `demo/order-management/src/repositories/inventoryRepository.ts` | +6 / -0 | 16-21 |
| `docs/ARCHITECTURE.md` | +48 / -6 | 77, 82, 97-100, 118-138, 165, 173-179, 193-200, 205-206, 208, 210-211 |
| `docs/DEMO.md` | +10 / -3 | 25, 45, 84-91 |
| `docs/EVALUATION.md` | +150 / -64 | 1, 5-8, 12-18, 20-22, 26-27, 36-46, 53-54, 60-61, 66-167, 176-177, 183, 187-190, 193, 197-202, 204-205 |
| `docs/HACKATHON_SUBMISSION.md` | +81 / -65 | 8-10, 15-18, 22-87, 91-97, 101 |
| `docs/STATUS.md` | +47 / -66 | 3-6, 12-18, 20-21, 24, 28-32, 36-51, 53-56, 58-60, 62-65, 69 |
| `frontend/src/api/client.ts` | +1 / -1 | 76 |
| `frontend/src/api/types.ts` | +2 / -2 | 79, 173 |
| `frontend/src/components/StartInvestigation.tsx` | +10 / -2 | 23, 120, 137-144 |
| `frontend/src/pages/Benchmarks.test.tsx` | +29 / -3 | 1, 9-10, 13-16, 37-58 |
| `frontend/src/pages/Benchmarks.tsx` | +30 / -17 | 7-8, 50-52, 57, 61-64, 69, 94-96, 103-106, 143-146, 151-154, 176, 178, 180, 182 |
| `frontend/src/pages/investigation/Report.tsx` | +7 / -3 | 54, 112-117 |
| `frontend/src/pages/investigation/Timeline.tsx` | +3 / -1 | 48, 50-51 |
| `frontend/src/pages/investigation/Workspace.tsx` | +1 / -1 | 61 |
