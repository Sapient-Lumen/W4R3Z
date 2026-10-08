# Architecture — rev0168

## Purpose

Revision 0168 is a final send-ready release-surface polish pass. It does not change the database schema, event schema, story ledger, scenario state machines, checkpoint custody, or provider boundaries. Its purpose is to make the archive's first public-facing screen accurately describe the current rev0167+rev0166 capability stack and to keep that entrance from drifting stale again.

## Surface under audit

The polished surface is deliberately small:

```text
README.md opening and release contents
START_HERE.md current-revision pointer
docs/README.md current revision records
docs/ROADMAP.md delivered/next framing
docs/design/GWERN_GIFT_TEST.md current research framing
tests/test_release_surface.py regression guard
REVISION.json / ACCEPTANCE_rev0168.json / MANIFEST.sha256
```

The three-door entrance remains unchanged: `PLAY_NOW.md` for the player, `FOR_GWERN.md` for the research claim, and `OPERATE_LACUNA.md` for the parent/operator.

## Retained architecture

Rev0168 retains:

- managed ordinary turn runs and source-bound checkpoint runs;
- fresh post-checkpoint narrator dispatches and narrator capsules;
- partial versus complete public-history custody;
- four-condition scenario runs and replicated bundles;
- whole-retained-tree canary scans before blind rating;
- post-primary-rating method-identifiability artifacts;
- bundle block seals that bind ratings, masking artifacts, and contamination scans;
- parent-opened bundle child unblind gates; and
- read-only extracted-artifact checks.

## Authority boundary

This revision adds no new worker power. Documentation, release records, and tests are sidecar/package custody. They do not mutate story state, attest providers, prove fresh memory, or evaluate narrative quality.
