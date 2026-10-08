# Example JSON snapshots should be addressable by stable ids or canonical surrogate ids

The archive now retains many small JSON examples: benchmark cards, receipts, handoff packets, bridge artifacts, and compact publication spines.
Those examples are useful only if future sessions can refer to them, inventory them, diff them, and attach small receipts to them **without first remembering schema-specific naming conventions**.

So every retained example JSON snapshot should expose one stable archive identity.
When the governing schema already allows an explicit `id`, keep it.
When the schema is intentionally strict and does not admit an extra `id` field, derive one canonical surrogate id from the retained repo-relative path instead of widening every schema just to satisfy one inventory check.

Why this belongs in the archive:

- `RS-GR-114` says machine-actionable metadata should stay easy for software systems to find and reuse, which supports making tiny example artifacts addressable instead of leaving identity implicit.
- `RS-GR-117` says lightweight machine-readable packaging benefits from explicit relations between constituent artifacts, which is easier once each example object has a stable local handle.
- `RS-GR-122` says FAIR metadata should carry globally unique identifiers, and `RS-GR-123` says RO-Crate entities must expose an identifier and that profiles improve reliable programmatic consumption.

Keep the discipline compact:

1. prefer explicit `id` fields where the schema already permits them;
2. otherwise synthesize one canonical surrogate id from the repo-relative path;
3. let inventories and duplicate-id checks operate over **explicit-or-surrogate** identities;
4. do not widen strict schemas just to satisfy a generic archive inventory.

This keeps the example corpus referenceable and validator-friendly without inflating the archive or forcing broad schema churn.
