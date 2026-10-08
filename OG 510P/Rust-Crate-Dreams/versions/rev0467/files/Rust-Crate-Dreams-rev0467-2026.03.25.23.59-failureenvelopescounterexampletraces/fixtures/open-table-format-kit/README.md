# open-table-format-kit fixtures

This fixture family makes **P-0028 open-table-format-kit** concrete as a support-contract lane instead of a vague “multi-format support” claim.

The point is to keep three truths reviewable:

1. **table-surface truth** — live catalog refresh vs static snapshot vs time-travel / incremental surfaces,
2. **capability-profile truth** — what reads, writes, maintenance actions, and engine registrations are honestly wired,
3. **integration-coupling truth** — whether the path is exact-version-coupled, FFI-decoupled, binding-wrapped, or carrying a storage/catalog gap.

These fixtures are intentionally tiny.
They are meant to prevent future archive passes from flattening current Iceberg / Delta / Hudi / DataFusion reality into one fake “supports open table formats” story.
