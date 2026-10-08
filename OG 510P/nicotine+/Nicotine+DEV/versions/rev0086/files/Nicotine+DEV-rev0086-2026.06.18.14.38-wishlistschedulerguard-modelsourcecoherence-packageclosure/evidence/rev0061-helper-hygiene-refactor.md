# Helper hygiene coherence refactor — rev0061

rev0061 found and repaired an inherited helper-smoke problem while doing the traceability closure pass.

## Finding

Running `tools/probe_rev0060_patch_order_permutation.py` from an extracted tree could import `probe_rev0059_patch_layer_attribution.py`, create `tools/__pycache__`, and then fail its own package-hygiene check because that check correctly rejects cache directories.

The underlying rev0060 patch-order evidence remains retained; the issue was a helper-hygiene false failure caused by the helper's own import-time side effect.

## Repair

rev0061 updates the inherited helper to:

```text
set sys.dont_write_bytecode before the local helper import
remove __pycache__ and .pytest_cache before package_hygiene()
```

The repaired inherited helper was rerun against the uploaded source bundle and passed. Output is stored in:

```text
evidence/rev0061-inherited-rev0060-helper-rerun-after-hygiene-fix.json
```

## Refactor boundary

This is a helper hygiene/refactor change only. It does not change selected patches, packet claims, regression expectations, or source-bundle boundaries.
