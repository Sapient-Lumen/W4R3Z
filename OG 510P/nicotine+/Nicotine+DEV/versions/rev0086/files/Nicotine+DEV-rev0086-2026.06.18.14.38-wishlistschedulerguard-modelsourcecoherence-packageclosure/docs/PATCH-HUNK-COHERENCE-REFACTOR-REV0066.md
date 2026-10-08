# Patch hunk coherence refactor — rev0066

rev0066 separates hunk-level patch-scope evidence from adjacent proof layers that had started to look similar in the cube.

## Separated layers

```text
rev0065 Git provenance/tree match:
  proves the uploaded source lanes bind to bundled Git refs, commits, and tree blobs.

rev0064 source intake:
  proves the ZIP can be safely identified and extracted.

rev0058 patch-file roundtrip:
  proves the generated patch files apply and reverse cleanly.

rev0059 split-patch attribution:
  proves each bundle carries its own regression fix and unrelated bundles do not.

rev0060 patch-order permutation:
  proves the bundle patches are order-safe.

rev0062 clean-room replay:
  proves the exported kit can replay outside cube-local helper paths.

rev0063 contract/tamper gate:
  proves the clean-room kit fails closed when required files or hashes are altered.

rev0066 hunk-scope/preimage binding:
  proves every exported patch hunk is scoped to expected files and matches the uploaded source preimage before rebuild.
```

## Audit result

No bundle scope drift was found.

The search-response source-admission patch remains distinct from the parser-budget patch even though both relate to FileSearchResponse handling. U-123 remains distinct from public path traversal and generic upload-spoofing language. PB-01 remains distinct from broad username/identity release-note language.
