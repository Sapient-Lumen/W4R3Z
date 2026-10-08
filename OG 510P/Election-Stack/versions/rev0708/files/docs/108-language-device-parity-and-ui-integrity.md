# Language/device parity and UI integrity

**Track:** A (Deployable core)


## Problem
An attacker can target non-majority languages or specific devices with:
- mistranslations
- missing warnings
- altered results banners

## Solution
Treat UI content as signed artifacts:
- locale bundles are content-addressed
- a `ContentLocaleManifest` binds locale strings and versioned assets

## Normative requirements
- **MUST** publish `ContentLocaleManifest` hashes and anchor them in checkpoints.
- **MUST** run parity probes across locales/device classes.
- **MUST** fail safe: if locale hash mismatch occurs, show “verification unavailable” and provide a safe fallback.

## Artifact
- `schemas/ContentLocaleManifest.json`