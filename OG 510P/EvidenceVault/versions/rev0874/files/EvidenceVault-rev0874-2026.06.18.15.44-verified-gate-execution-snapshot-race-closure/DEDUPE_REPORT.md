# Deduplication report

This governed report is regenerated from the shipped tree by `python3 scripts/build_dedupe_report.py` and checked by `python3 scripts/validate_dedupe_report.py`.

Scope excludes `DEDUPE_REPORT.md`, `SBOM/EvidenceVault-file-inventory.spdx.json`, `MANIFEST.sha256`, `INDEX/files.json`, and `INDEX/files.csv` to avoid generated-surface digest/count loops.

## Current duplicate-payload summary

- Files scanned: **4584**
- Unique blobs by SHA-256: **4124**
- Duplicate copies: **460**
- Duplicate bytes, counting only extra copies: **3762513** (~3.59 MiB)

## Deduplication policy

- Exact duplicate detection is advisory unless a duplicate is already covered by a canonical-path pointer or a governed mirror policy.
- Root paper PDF mirrors are intentionally duplicated from `papers/*.pdf` and are separately checked by `scripts/validate_paper_series.py`.
- Retained upstream snapshots, audit trails, and content-addressed bundle stores may intentionally retain duplicate blobs because collapsing them can obscure provenance.
- Curated exact mirrors should use `CANONICAL_PATHS.json` when a retained canonical owner exists and the rehydration path is clear.

## Largest duplicate blobs (top 20)

| count | size each (bytes) | duplicate bytes | sha256 | example paths |
|---:|---:|---:|---|---|
| 2 | 484300 | 484300 | `fe7cebe939df9ccd12c471ce9eceb3c186fbc5102cf201a36b28380c3fb18d05` | sources/ocf_llm/archive/v264_snapshot/paper.tex; sources/ocf_llm/paper.tex |
| 2 | 249321 | 249321 | `7e6baf39d9c64b37344d3c8ebfd03fdf5b64f4542267c8d2e5bad5a76fed1bc8` | ev_interpretation_profiles.pdf; papers/ev_interpretation_profiles.pdf |
| 2 | 249005 | 249005 | `665c2f68b0e3c9a43783e88aaf39ebf120f7cdd864d9d93b00b326256df0d914` | ev_acceptability_kernel.pdf; papers/ev_acceptability_kernel.pdf |
| 2 | 166145 | 166145 | `e5a8d8b4c9da31c35565181a17c47adaac03a362008cbd1c5be44b4b589a4488` | ev_zkrtp.pdf; papers/ev_zkrtp.pdf |
| 2 | 151377 | 151377 | `8903c85da120f6a02268fb9416a382e7bd7f71b5d6f6cc0eb46d636c0614fe1d` | sources/ocf_llm/archive/v264_snapshot/references.bib; sources/ocf_llm/references.bib |
| 2 | 138610 | 138610 | `c9e44fc2e390f416a6fc6dae10a09eb77bab826fe402bd323786a579dd28c0b9` | ev_streamfold.pdf; papers/ev_streamfold.pdf |
| 2 | 137775 | 137775 | `1d614902fc71d0da6344265d829e50b085b834419d9bb1295667a413060996cc` | sources/ocf_llm/archive/v250_snapshot/references.bib; sources/ocf_llm/archive/v251_snapshot/references.bib |
| 2 | 128134 | 128134 | `14228720f27c385d3b02f26e91680c604cd47ac6c338372d65b7ebc565c5c9cf` | ev_pact_ocf.pdf; papers/ev_pact_ocf.pdf |
| 2 | 116287 | 116287 | `50d8b60372aa077b48e17fbfa0855b71e5b0ef4b6a85d3f59a06ca3af31098ae` | sources/ocf_llm/archive/v264_snapshot/notes.md; sources/ocf_llm/notes.md |
| 4 | 34855 | 104565 | `955aa541007e268a387474c30af54326460c57392fd18f8f6f655722816e576e` | sources/ocf_llm/examples/monitoring_elond_evalues_v153.jsonl; sources/ocf_llm/examples/monitoring_elond_evalues_v156.jsonl; sources/ocf_llm/examples/monitoring_elond_evalues_v157.jsonl; sources/ocf_llm/examples/monitoring_elond_evalues_v158.jsonl |
| 3 | 46255 | 92510 | `93d76b9ee6af23d99051e8fe3bf9a3b4539dd38d28bd233580c5acd4abac4720` | sources/ocf_llm/archive/v256_snapshot/examples/idc_synth_bench_v256/reports/rep_some_unique_n80_v2.json; sources/ocf_llm/examples/idc_synth_bench_v256/reports/rep_some_unique_n80_v2.json; sources/ocf_llm/examples/idc_synth_bench_v257/reports/report_some_unique_n80.json |
| 6 | 18256 | 91280 | `75d05e53b92cfd9fc692b1c6d24a838d284e7af1f865aadaac4e052e3dcbf81f` | sources/ocf_llm/examples/change_control_demo_v207/cache_policy.json; sources/ocf_llm/examples/drift_budget_demo_v203/cache.json; sources/ocf_llm/examples/interface_drift_delta_cert_demo_v200/receipts.json; sources/ocf_llm/examples/interface_drift_delta_cert_demo_v201/cache.json ... |
| 2 | 85760 | 85760 | `1a8049b9a0b550c69195fa45b8c8a95bbefe2adc4198a6b44ba14bf403dc0511` | sources/ocf_llm/archive/v256_snapshot/figs/idc_synth_cost_one_shared_v256.png; sources/ocf_llm/figs/idc_synth_cost_one_shared_v256.png |
| 2 | 84519 | 84519 | `3fd649f8e26380e45a4827ef112047409864e79e9ccc67b9c690f4952e20bbbe` | sources/ocf_llm/archive/v256_snapshot/figs/idc_synth_cost_some_unique_v256.png; sources/ocf_llm/figs/idc_synth_cost_some_unique_v256.png |
| 2 | 81709 | 81709 | `226ef1c73004ec9c0a40bf6f8a4681cfe862bd921cc1402859bf97ff4c3bf059` | sources/ocf_llm/archive/v256_snapshot/figs/idc_synth_cost_none_v256.png; sources/ocf_llm/figs/idc_synth_cost_none_v256.png |
| 3 | 35890 | 71780 | `1d823a854e678fd5c44e0c3750f281ca5219a886b11d6e4f9de465f21c160c9e` | sources/ocf_llm/examples/crypto_attempts_log_v156.jsonl; sources/ocf_llm/examples/crypto_attempts_log_v157.jsonl; sources/ocf_llm/examples/crypto_attempts_log_v158.jsonl |
| 3 | 32928 | 65856 | `caa88ce3197e99487a1931fde020f9f7aaf009fc4e5077e5ad39f7312290d284` | sources/ocf_llm/examples/change_control_demo_v207/cache_resolution.json; sources/ocf_llm/examples/release_train_demo_v209/cache_resolution.json; sources/ocf_llm/examples/resolution_drift_debt_demo_v206/cache.json |
| 3 | 31970 | 63940 | `ec0a5e96875080aea345cb2f79a003f3e24d648a3ca43a9cf3a07a9c437aaabf` | sources/ocf_llm/archive/v256_snapshot/examples/idc_synth_bench_v256/profiles/synth_v2_n80.json; sources/ocf_llm/examples/idc_synth_bench_v256/profiles/synth_v2_n80.json; sources/ocf_llm/examples/idc_synth_bench_v257/profiles/synth_v2_n80.json |
| 3 | 28038 | 56076 | `d3244548094d1c9f9d4a7bb515092c4ff0c79824cab2d0746e45020d0ebb72ab` | artifacts/repro_packs/acceptance_delta_repro_pack/artifacts/transparency_log_example.json; artifacts/repro_packs/acceptance_repro_pack/artifacts/transparency_log_example.json; artifacts/repro_packs/acceptance_semantic_repro_pack/artifacts/transparency_log_example.json |
| 2 | 51647 | 51647 | `14fa1622c0b4c68a381e309f40e5a6969047471e297a4bba82917bbd6e9f1447` | artifacts/repro_packs/acceptance_repro_pack/artifacts/review_draw_witness_example.json; artifacts/repro_packs/acceptance_semantic_repro_pack/artifacts/review_draw_witness_example.json |

## Notes

- This report is intentionally a measured inventory, not an instruction to remove every duplicate.
- Future pruning should prefer explicit canonical-path ledgers plus absence/provenance ledger updates over silent deletion.
