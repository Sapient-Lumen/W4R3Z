# Residual path portability rewrite — rev0831

This ledger records the explicit, non-heuristic rewrites used to remove the remaining cloud/container path coordinates after rev0830.

- Status: `residual_cloud_paths_rewritten_or_relabelled`
- Replacement rules: **19**
- Files touched: **16**
- Occurrences rewritten: **22**

## Classifications

- `historical_unretained_build_root_label`
- `preserve_serialized_path_object_bug_without_cloud_root`
- `rewrite_benchmark_base_to_archive_root`
- `rewrite_benchmark_base_to_shipped_source_root`
- `rewrite_file_uri_to_archive_relative_locator`
- `rewrite_missing_artifact_reference_to_relative_expected_path`
- `rewrite_prefix_map_to_shipped_source_root`
- `rewrite_to_existing_shipped_directory`
- `rewrite_to_existing_shipped_file_inside_captured_output`

## Rewrite rows

| Path | Count | Classification | Old | New |
| --- | ---: | --- | --- | --- |
| `artifacts/curated/zkrtp_v2/policy_report.json` | 1 | `historical_unretained_build_root_label` | `/mnt/data/zk_rtp_paper_v0.27` | `unretained-upstream:zk_rtp_paper_v0.27` |
| `sources/ocf_llm/examples/mer_demo/receipt_cache_index.json` | 1 | `rewrite_to_existing_shipped_directory` | `/mnt/data/ocf_llm_paper_v196_work/ocf_llm_paper_evolving_v196/examples/mer_demo/receipt_cache` | `sources/ocf_llm/examples/mer_demo/receipt_cache` |
| `sources/ocf_llm/examples/nuc_demo/receipt_cache_ok_index.json` | 1 | `rewrite_to_existing_shipped_directory` | `/mnt/data/ocf_llm_paper_v197_work/ocf_llm_paper_evolving_v197/examples/nuc_demo/receipt_cache_ok` | `sources/ocf_llm/examples/nuc_demo/receipt_cache_ok` |
| `sources/ocf_llm/examples/pip_gate_decision_annexiv_tampered_v1.json` | 1 | `rewrite_prefix_map_to_shipped_source_root` | `ocf/paper/=/mnt/data/ocf_llm_paper_v97/` | `ocf/paper/=sources/ocf_llm/` |
| `sources/ocf_llm/examples/pip_gate_decision_annexiv_v1.json` | 1 | `rewrite_prefix_map_to_shipped_source_root` | `ocf/paper/=/mnt/data/ocf_llm_paper_v97/` | `ocf/paper/=sources/ocf_llm/` |
| `sources/ocf_llm/examples/prc_put_demo_v203/prc.json` | 1 | `rewrite_file_uri_to_archive_relative_locator` | `file:///mnt/data/ocf_llm_paper_evolving_current_v203/examples/prc_put_demo_v203` | `archive-relative:sources/ocf_llm/examples/prc_put_demo_v203` |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_rec.yaml` | 1 | `rewrite_missing_artifact_reference_to_relative_expected_path` | `/mnt/data/ocf_llm_paper_evolving_current_v123/ocf_llm_paper_evolving/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl` | `sources/ocf_llm/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl` |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_scitt.yaml` | 1 | `rewrite_missing_artifact_reference_to_relative_expected_path` | `/mnt/data/ocf_llm_paper_evolving_current_v123/ocf_llm_paper_evolving/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl` | `sources/ocf_llm/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl` |
| `sources/ocf_llm/examples/release_train_overlap_demo_v211/summary.json` | 1 | `rewrite_to_existing_shipped_directory` | `/mnt/data/ocf_llm_paper_evolving_current_v211/examples/release_train_overlap_demo_v211` | `sources/ocf_llm/examples/release_train_overlap_demo_v211` |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | 1 | `rewrite_benchmark_base_to_shipped_source_root` | `/mnt/data/ocf_llm_paper_v87` | `sources/ocf_llm` |
| `sources/ocf_llm/examples/resolver_bench_v2.json` | 1 | `rewrite_benchmark_base_to_archive_root` | `/mnt/data/ocf_llm_paper_workspace_v91/ocf_llm_paper_v90` | `.` |
| `sources/ocf_llm/examples/resolver_bench_v3.json` | 1 | `rewrite_benchmark_base_to_archive_root` | `/mnt/data/ocf_llm_paper_workspace_v91/ocf_llm_paper_v90` | `.` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm.yaml` | 3 | `preserve_serialized_path_object_bug_without_cloud_root` | `/mnt/data/ocf_llm_v81_work/ocf_llm_paper/examples/{'kind': 'file', 'path': 'examples/scitt_receipt_refusal_map_root_v1.json'}` | `sources/ocf_llm/examples/{'kind': 'file', 'path': 'examples/scitt_receipt_refusal_map_root_v1.json'}` |
| `sources/ocf_llm/examples/runtime_gate_bench_v1.json` | 1 | `rewrite_to_existing_shipped_file_inside_captured_output` | `/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_eval_log_v1.jsonl` | `sources/ocf_llm/examples/eic_qic_latency_eval_log_v1.jsonl` |
| `sources/ocf_llm/examples/runtime_gate_bench_v1.json` | 1 | `rewrite_to_existing_shipped_file_inside_captured_output` | `/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_suite_v1.jsonl` | `sources/ocf_llm/examples/eic_qic_latency_suite_v1.jsonl` |
| `sources/ocf_llm/examples/runtime_gate_bench_v1.json` | 2 | `rewrite_to_existing_shipped_file_inside_captured_output` | `/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_summary_v1.json` | `sources/ocf_llm/examples/eic_qic_latency_summary_v1.json` |
| `sources/ocf_llm/examples/runtime_gate_bench_v1.json` | 1 | `rewrite_benchmark_base_to_shipped_source_root` | `/mnt/data/ocf_llm_paper_v96` | `sources/ocf_llm` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_base_pinned.yaml` | 1 | `rewrite_missing_artifact_reference_to_relative_expected_path` | `/mnt/data/ocf_llm_paper_evolving_current_v125/ocf_llm_paper_evolving/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json` | `sources/ocf_llm/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_base_unpinned.yaml` | 1 | `rewrite_missing_artifact_reference_to_relative_expected_path` | `/mnt/data/ocf_llm_paper_evolving_current_v125/ocf_llm_paper_evolving/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json` | `sources/ocf_llm/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json` |

## Notes

- Rewrites with `rewrite_missing_artifact_reference_to_relative_expected_path` intentionally keep the referenced target absent; the point is portability of the expected path, not conversion of a negative test into a passing test.
- The serialized-object path anomaly is intentionally not normalized into an existing receipt path because that would silently change a historical fail-closed trace. It is surfaced separately by `AUDIT/PATH_REFERENCE_SHAPE_AUDIT.*`.
- The zk-RTP build root is relabelled as `unretained-upstream:*` because the full upstream root is not retained in this archive.
