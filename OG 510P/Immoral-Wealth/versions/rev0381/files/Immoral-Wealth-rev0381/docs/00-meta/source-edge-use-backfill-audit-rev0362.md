---
project: Immoral Wealth
status: source_edge_use_backfill_audit
revision_current: rev0368
generated_at: 2026-06-18T14:06:00Z
---

# Source-edge use backfill audit — rev0362

The refactor found a trust risk: a source could support a live case citation while its source row still looked unused by cases. Rev0362 recomputes `used_by_cases` and `used_by_fields` from scoreboards and case memos, touching **16 source rows**, and added **5** memo-level citation associations solely to preserve lineage. These rows are not proof.

New current-law sources added: **S542-S545**.
