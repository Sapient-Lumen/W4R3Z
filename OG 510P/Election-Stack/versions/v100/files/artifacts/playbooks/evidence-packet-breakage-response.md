# Evidence Packet Breakage / Format Drift Response Playbook

## When to use
Use when independent verifiers cannot validate published evidence due to:
- missing objects referenced by manifest,
- incompatible schema/envelope versions,
- corrupted mirrors,
- or refactors that broke link stability.

## Immediate steps (0–24h)
1. **Freeze publication inputs**
   - stop replacing bundles in-place
   - snapshot current mirrors
2. **Rebuild from source**
   - run `scripts/build_manifest.py`
   - regenerate schema catalog: `scripts/gen_schema_catalog.py`
3. **Produce a corrected evidence packet**
   - pack with `tools/evidence_packager.py`
   - publish a new packet id; do not overwrite the old one
4. **Publish a tombstone/alias note**
   - point old ids to new packet ids (append-only)

## Escalation (24–72h)
5. **Independent reproduction**
   - ask at least two external verifiers to validate the corrected packet
6. **Root-cause analysis**
   - identify: schema drift, toolchain drift, missing files, mirror corruption

## Recovery
7. **Backfill missing artifacts**
   - if artifacts are unrecoverable, publish a signed spoliation notice with digests of what is missing

## Long-term fixes
- tighten the release gate in `docs/162`
- ensure every schema change is paired with:
  - a version bump,
  - an ADR,
  - and a compatibility note
