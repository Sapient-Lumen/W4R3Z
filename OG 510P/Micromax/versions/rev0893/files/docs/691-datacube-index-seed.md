# Datacube revision-index seed (rev748)

Rev748 adds `docs/revision-index.json` as a small machine-readable seed for the datacube-index idea.

The existing prose ledger remains valuable because it preserves intent, taste, and handoff history.  The index is not meant to replace that trail.  It gives future humans, scripts, and LLMs a compact entry point for the current landing:

- revision number and tag
- trust/product intent
- touched surfaces
- docs and code paths
- guarantees
- risks
- recommended next seams

The first entry records rev748 only.  Future landings can append one compact object per revision instead of forcing every reader to scan the large append-only docs before discovering what changed.

## Shape

```json
{
  "schema": "micromax.revision-index.v1",
  "current_rev": 748,
  "entries": [
    {
      "rev": 748,
      "intent": ["trust", "installed-package-semantics"],
      "surfaces": ["VM-startup", "mxtest"],
      "guarantees": ["..."],
      "risks": ["..."]
    }
  ]
}
```

The immediate rule is modest: `current_rev` should match the repo context revision, and the newest entry should point at the docs/code paths that explain the landing.
