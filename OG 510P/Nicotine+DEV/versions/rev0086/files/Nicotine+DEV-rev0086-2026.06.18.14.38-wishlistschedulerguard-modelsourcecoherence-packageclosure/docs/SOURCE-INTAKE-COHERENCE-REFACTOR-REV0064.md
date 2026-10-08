# Source-intake coherence refactor — rev0064

rev0064 adds a new layer to the evidence stack: **source-bundle intake and safe extraction**. This refactor keeps that layer separate from the surrounding proof types.

## Refactor split

| layer | rev0064 treatment | why it stays separate |
|---|---|---|
| Uploaded source-bundle identity | New rev0064 gate | Establishes exactly which archived source ZIP was consumed. |
| ZIP entry/path safety | New rev0064 gate | Prevents accidental trust in unsafe archive paths or symlink entries. |
| Source-lane file manifests | New rev0064 gate | Captures every lane file hash without embedding source content. |
| Critical touched-file hashes | Crosschecked against rev0051 | Confirms the strict/front source anchors and source intake describe the same archived lanes. |
| Safe extraction roundtrip | New rev0064 gate | Proves the helper can extract source lanes with count/hash parity. |
| Clean-room positive replay | Inherited rev0062 | Shows exported patches/tests replay outside the cube. |
| Clean-room contract/tamper controls | Inherited rev0063 | Shows the exported kit fails closed on missing/unsafe/tampered inputs. |
| Patch order/attribution/roundtrip | Inherited rev0058–rev0060 | Shows patch artifacts work and remain attributable. |
| Traceability closure | Inherited rev0061 | Maps packets to claim, anchor, regression, patch, and handoff artifacts. |
| Current-web marker snapshots | Inherited rev0054 | Useful public snapshot only; not a source checkout. |
| Fresh current checkout/tarball proof | Still pending | Required before live-current external filing. |

## Decision

No private packet was promoted or retired. The seven production-gated packets remain frozen. rev0064 only hardens the archived-source input path used by the existing gates.

## Queue impact

The next queue remains current-source oriented:

```text
1. Obtain a fresh current checkout or current source tarball with commit/hash/date.
2. Run the current-source gate and classify the seven packets.
3. Adapt split patches only if selected-patch-still-needed on current source.
4. Use rev0064 source-intake, rev0063 contract/tamper, rev0062 clean-room replay, and rev0061 traceability as archived-source evidence layers.
```
