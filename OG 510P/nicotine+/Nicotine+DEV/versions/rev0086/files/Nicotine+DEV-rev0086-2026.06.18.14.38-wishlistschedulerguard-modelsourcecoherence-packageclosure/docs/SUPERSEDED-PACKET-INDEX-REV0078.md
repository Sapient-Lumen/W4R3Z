# Superseded packet and mechanism index — rev0078

## SEARCH-AGAIN-EPOCH-01

No full refresh patch is selected. Rev0077's pure epoch examples are preserved as preliminary countermodels; rev0078's current authority is `docs/SEARCH-AGAIN-EPOCH-01-CURRENT-DISPOSITION-REV0078.md` and the executable packet under `maintainer_artifacts/search-epoch-01/`.

The rev0077 one-line `SEARCH-AGAIN-SELF-01` bookkeeping patch remains selected only for that closed, narrow research disposition. It must not be misread as a refresh implementation.

## Current package tooling

Revision-specific manifest and delta builders through rev0077 remain historical evidence. Current entrypoints are:

```text
tools/build_current_manifest.py
tools/build_current_delta_inventory.py
tools/audit_current_package.py
tools/cube_runtime.py
```

## Earlier packets

The supersession judgments from rev0077 remain unchanged:

```text
SEARCH-RESP-01B: rev0040 production-ready language remains superseded by rev0076.
SEARCH-RESP-01A: rev0039 production-ready language remains superseded by rev0075.
PB-01:            rev0038 blanket guard remains superseded by rev0074.
U-123:            selected artifact remains research-only under rev0073.
```
