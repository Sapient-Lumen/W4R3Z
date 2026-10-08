# Upstream retention coverage

This is the current-release boundary surface for shipped retained sources. It deliberately separates historical upstream-diff matching from what is actually present under the shipped `sources/` tree.

Inputs: `SOURCE_INDEX.json`, `AUDIT/UPSTREAM_DIFF_REPORT.md`, and the actual `sources/` filesystem.

## Summary

- Projects checked: **7**
- Historical/audit-workspace source matches: **12072**
- Shipped retained source files: **3476**
- Retention drift files: **8596**
- Projects with retention drift: `pact`, `ocf_llm`, `streamfold`, `zkrtp_portfolio`, `zkrtp_v2`

## Project table

| Project | Status | Historical source matches | Shipped retained root | Shipped retained files | Drift | Action |
| --- | --- | ---: | --- | ---: | ---: | --- |
| `ctg` | `retained_source_root` | 90 | `sources/ctg` | 90 | 0 | `ok` |
| `docf` | `retained_source_root` | 658 | `sources/docf` | 658 | 0 | `ok` |
| `pact` | `retained_source_root` | 705 | `sources/pact` | 620 | 85 | `relabel_historical_report_or_regenerate_from_shipped_tree` |
| `ocf_llm` | `retained_source_root` | 2113 | `sources/ocf_llm` | 2108 | 5 | `relabel_historical_report_or_regenerate_from_shipped_tree` |
| `streamfold` | `represented_without_retained_source_root` | 4733 | `sources/streamfold` | 0 | 4733 | `relabel_historical_report_or_regenerate_from_shipped_tree` |
| `zkrtp_portfolio` | `represented_without_retained_source_root` | 2473 | `sources/zkrtp_portfolio` | 0 | 2473 | `relabel_historical_report_or_regenerate_from_shipped_tree` |
| `zkrtp_v2` | `represented_without_retained_source_root` | 1300 | `sources/zkrtp_v2` | 0 | 1300 | `relabel_historical_report_or_regenerate_from_shipped_tree` |

## Interpretation

A nonzero drift value does not by itself prove data loss. It proves that an upstream-diff matching count is not the same thing as current shipped retained-source coverage. For represented families such as StreamFold and zk-RTP, the correct shipped count can be zero if the family is intentionally represented by curated artifacts, certificates, papers, and legacy renders instead of a retained `sources/` root.

The release gate should fail if this file stops exactly matching the current filesystem or if `AUDIT/UPSTREAM_DIFF_REPORT.md` reintroduces the ambiguous old present-in-sources claim without the historical/audit-workspace qualifier.
