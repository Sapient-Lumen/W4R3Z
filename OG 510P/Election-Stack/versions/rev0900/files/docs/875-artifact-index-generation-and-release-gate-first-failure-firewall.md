# Artifact-index generation and release-gate first-failure firewall

**Track:** Shared / Release gate / Artifact index
**Status:** v855/v856 release-gate coherence repair

## Problem fixed in v855

The rev0854 archive carried a dangerous release-gate regression: `scripts/check_index.py` failed before the gate reached verifier, source, packaging, or manifest checks because `docs/13-artifact-index.md` had been collapsed into a short current-head summary. That looked readable, but it removed the old invariant that every canonical numbered doc must be discoverable from the artifact index.

The failure was useful because it exposed a real maintenance smell: a hand-maintained index for a 900+ doc cube is not a tractable release-control surface. The correction is to make the index generated and then check it.

## v855 change

v855 adds `scripts/gen_artifact_index.py` and runs it before `scripts/check_index.py` in the canonical release-gate inventory. The generator rewrites `docs/13-artifact-index.md` from the tree itself and includes every non-tombstone numbered doc under `docs/`.

The release-gate invariant is now:

```text
scripts/gen_artifact_index.py -> scripts/check_index.py -> rest of release gate
```

This keeps the index usable as a current release router while preventing a future concise hand edit from silently deleting canonical coverage.

## Why this is substantive, not bureaucracy

This correction does not add a new policy family. It removes a known release-gate first-failure and turns a high-maintenance hand list into generated state. That is the difference between a real release-control surface and another place where the cube can look polished while being stale.

## Non-claims

The generated artifact index is only a navigation and release-coherence artifact. It does not prove current voter instructions, legal authority, certification, production signer authority, independent validation, or live-pilot readiness.
