---
project: Immoral Wealth
status: validator_history_refactor_audit
revision_current: rev0370
generated_at: 2026-06-18T10:01:38Z
---

# Validator history refactor audit — rev0358

The validator still contains **79** check functions, including **47** release-specific checks. That is a real maintenance risk: old revision fixtures can freeze current behavior and block substantive migration.

Rev0358 applies one concrete repair: the rev0357 check is converted from a live-state assertion (`verified_claim_edge_count` must always be zero) into a historical assertion about the rev0357 report. That allows the archive to make real evidence progress without rewriting rev0357 history.

Next refactor: move release snapshots into a data ledger and keep executable validation focused on generic invariants.
