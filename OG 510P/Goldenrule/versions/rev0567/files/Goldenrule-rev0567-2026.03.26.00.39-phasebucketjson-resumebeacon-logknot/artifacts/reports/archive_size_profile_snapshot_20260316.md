# Archive size profile snapshot — 2026-03-16

Focus: measure the retained archive footprint so future inheritors can keep the archive citation-first and compact without losing reproducibility

## Headline findings
- The archive currently holds 1487 retained files at 11164120 raw bytes (10.647 MiB) and compresses to about 3038782 bytes (2.898 MiB) in a revision zip.
- The `artifacts/reports` bucket is the main retained growth surface at 207752 raw bytes (0.198 MiB), or 0.018609 share of the raw tree.
- Report fanout is mostly duplicated presentation surfaces: 0 JSON+MD report pairs consume 0 raw bytes (0.0 MiB), which is 0.0 share of the reports bucket.
- The largest retained file is `docs/AGENT_LOG.md` at 596396 bytes; the next two are `CHANGELOG.md` and `docs/AGENT_LOG.md`, so internal operational surfaces now matter more than literature blobs.
- The prior PDF compaction removed 47925095 bytes (45.705 MiB), so the archive's next size risk is internal report/log fanout rather than external reading packs.

## Archive totals
- retained files: `1487`; raw footprint: `11164120` bytes (`10.647` MiB); approx revision zip: `3038782` bytes (`2.898` MiB).

## Artifact buckets
| bucket | files | raw bytes | raw MiB | share of raw tree |
|---|---:|---:|---:|---:|
| timing | 4 | 8333 | 0.008 | 0.000746 |
| security | 2 | 429 | 0.0 | 3.8e-05 |
| process | 9 | 86908 | 0.083 | 0.007785 |
| release | 2 | 1843 | 0.002 | 0.000165 |
| formal | 2 | 81255 | 0.077 | 0.007278 |
| reports | 19 | 207752 | 0.198 | 0.018609 |

## Report fanout
- JSON+MD pairs: `0`; pair bytes: `0`; pair share of report bucket: `0.0`.

## Largest retained files
- `docs/AGENT_LOG.md` — `596396` bytes (`0.569` MiB)
- `CHANGELOG.md` — `567036` bytes (`0.541` MiB)
- `Original-Starting-Place/sandworm` — `250995` bytes (`0.239` MiB)
- `scripts/analysis/rematch_proxy_delta_decision_packet.py` — `233246` bytes (`0.222` MiB)
- `scripts/tools/build_archive_report_semantic_handle_receipt.py` — `128003` bytes (`0.122` MiB)
- `grlab/cli.py` — `93667` bytes (`0.089` MiB)
- `docs/RESEARCH_SOURCES.md` — `81348` bytes (`0.078` MiB)
- `artifacts/formal/certify_invariants.json` — `81097` bytes (`0.077` MiB)
- `grlab/certify.py` — `79660` bytes (`0.076` MiB)
- `examples/snapshots/rematch_world_benchmark_compiled_artifact.json` — `79229` bytes (`0.076` MiB)

## Largest report families
- `cooperation_benchmark_card_scope_surface` — `1` files, `49683` bytes (`0.047` MiB)
- `validator_inventory` — `1` files, `28949` bytes (`0.028` MiB)
- `cooperation_benchmark_card_taxonomy` — `1` files, `26178` bytes (`0.025` MiB)
- `examples_validation` — `1` files, `17712` bytes (`0.017` MiB)
- `cooperation_benchmark_card_next_action` — `1` files, `16080` bytes (`0.015` MiB)
- `cooperation_benchmark_card_next_action_witness` — `1` files, `15392` bytes (`0.015` MiB)
- `cooperation_benchmark_card_handoff_pack` — `1` files, `12588` bytes (`0.012` MiB)
- `schema_inventory` — `1` files, `10479` bytes (`0.01` MiB)
- `cooperation_benchmark_card_control_plane` — `1` files, `9736` bytes (`0.009` MiB)
- `cooperation_benchmark_card_inventory` — `1` files, `5630` bytes (`0.005` MiB)

## Recommendations
- Keep external literature in citation-first mode and reacquire PDFs only as temporary scratch.
- Treat `artifacts/process/scratch_manifest.json` as the retained handoff index for any temporary scratch that survives a session boundary.
- When a pass does not create a standing contract or validator, prefer one canonical machine-readable artifact plus a short inheritor note over another large JSON+MD report pair.
- Refresh `artifact_summary.json` and `ARTIFACT_BUCKETS.md` after archive-shaping edits so future sessions can see footprint drift immediately.

## Source reports
- `artifacts/process/archive_compaction_20260306.json`
- `scripts/report/build_archive_size_profile_snapshot.py`
