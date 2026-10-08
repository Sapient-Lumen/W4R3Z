# Scenario: rustdoc JSON opaque IDs need item witnesses, not cross-blob reuse

Problem:
A tool imported two crate-knowledge bundles and noticed the same-looking rustdoc JSON item ID string.
It wants to treat that as proof of stable identity across bundles.

Why this scenario exists:
RFC 2963 explicitly says rustdoc JSON IDs are opaque, only valid within a single JSON blob, and not guaranteed to be stable across compiler invocations.

What must be proven instead:
- the exact crate version,
- the exact target,
- the item path and kind,
- and, when available, source-span context plus locator edges.

What this example proves:
A proper witness manifest can record the observed opaque ID while still marking its scope as blob-local and refusing to treat it as a durable cross-bundle identifier.
