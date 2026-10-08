# Operational risk retirement — rev0864

This pass closes work that can be completed from evidence and retires work that cannot.

## Substantive closure

The only known broken local license reference is repaired with exact upstream bytes. The count is now **0**, while the root publication blocker remains explicit.

## StreamFold patch archaeology: stop condition reached

All **25** parent patch files were searched for exact diff sections for the **17** expected StreamFold payload paths (25066 bytes total). Paths and hashes appear in metadata, but **zero** target paths have their own patch diff section. Therefore these patches do not contain reconstructable target payload bodies. Further patch-history search is low-value unless a new base or source artifact appears.

## Command-surface refactor

Use one command:

```bash
python3 scripts/overlay_gate.py
```

It reads structured checks from `PATCH_BUNDLE_MANIFEST.json`, invokes them without a shell, captures results, and fails on any required check. The canonical `Makefile` is deliberately unchanged because this overlay does not carry its full script surface.

## Next real dependencies

The remaining high-risk work is externally dependent: an owner rights decision and actual StreamFold candidate bytes/full canonical tree. Another doctrine or search lane without either input would be churn.
