---
project: Immoral Wealth
status: field_retirement_cutover_audit
revision_current: rev0368
generated_at: 2026-06-18T14:06:00Z
---

# Field retirement cutover audit — rev0360

Rev0360 removes **50 zero-use registered_unused fields** from the closed scoreboard schema, field registry, and field-use ledger.

Before: 367 registered fields / 50 registered_unused fields.  
After: **317 registered fields / 0 registered_unused fields**.

No low-use nonzero field was removed. No case payload was edited. No verdict was upgraded. This is a cleanup of false schema surface area, not a doctrine expansion.

Retired IDs are recorded in `docs/00-meta/field-retirement-cutover-audit-rev0360.json`.
