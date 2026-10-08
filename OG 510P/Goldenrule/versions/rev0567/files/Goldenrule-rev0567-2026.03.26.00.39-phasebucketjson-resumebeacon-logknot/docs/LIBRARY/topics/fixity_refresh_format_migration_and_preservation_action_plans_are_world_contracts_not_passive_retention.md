# Fixity refresh, format migration, and preservation action plans are world contracts, not passive retention

Recent work adds another missing layer to Concord's long-horizon archive and stewardship worlds: **it matters whether future stewards inherit a repository that keeps checking integrity, repairing corruption, revisiting format risk, and planning migrations for unsustainable formats — rather than assuming that once bytes are stored they remain trustworthy and usable forever**.

- `RS-GR-326` shows that NARA treats fixity generation, annual fixity audits, repair / replacement of damaged files, replication, lifecycle logging, and preservation action plans for unsustainable formats as part of the preservation institution itself.
- `RS-GR-327` shows that NARA refreshes its Digital Preservation Framework and republishes updated file-format preservation action plans on a continuing quarterly cadence.
- `RS-GR-328` shows that repository trustworthiness is audited against ISO 16363 as a repeated self-assessment practice rather than assumed once and then forgotten.
- Together, these sources warn that a benchmark can look more durable, more successor-safe, or more future-protective because it changed **fixity-refresh cadence, repair duty, format-risk review, preservation-action planning, or trust-audit refresh** — not because the underlying Golden-Rule disposition improved.

## Why this matters for Concord

A future-facing benchmark should not report that an institution “preserves things for successors” when the world mainly changed its **active preservation architecture**.

There is a real institutional difference between:
1. a world that stores files once and never rechecks them;
2. a world that computes checksums only at ingest;
3. a world that runs recurring fixity audits but lacks clear repair authority;
4. a world that combines integrity refresh, repair / replacement, format-risk review, and preservation action plans; and
5. a world that looks durable only because it maintains active preservation loops rather than because agents became more future-regarding.

Those are not archival housekeeping details.
They change whether successors inherit merely retained bytes or evidence-backed, still-usable records.

## Minimal implementor handoff

If Concord adds archive, repository, or long-horizon stewardship lanes, publish at least:

1. whether integrity is checked only at ingest or also through recurring audits;
2. whether failed integrity checks trigger repair, replacement, quarantine, or mere logging;
3. whether format sustainability is reviewed on a cadence and whether unsustainable formats have action plans;
4. whether repository trustworthiness is periodically audited or only assumed;
5. whether headline results survive one same-behavior comparison where only fixity-refresh / format-migration semantics change.

Without that compact contract, future inheritors can mistake active preservation machinery for the same thing as deeper reciprocity toward successors.
