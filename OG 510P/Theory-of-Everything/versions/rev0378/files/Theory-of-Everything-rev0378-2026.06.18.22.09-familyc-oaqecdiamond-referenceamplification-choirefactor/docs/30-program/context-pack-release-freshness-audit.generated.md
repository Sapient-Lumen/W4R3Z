# Context-pack release freshness audit (generated)

Generated from `context-pack.json`, `RELEASE-MANIFEST.json`, and `REVISION-RECEIPT.json`. Do not edit directly; run `make index` after changing restart handoff or release identity surfaces.

- Manifest revision: `rev0378`
- Checks: `11`
- Freshness failures: `0`

| Check | Expected | Actual | Pass |
|---|---|---|---:|
| `context.revision` | `rev0378` | `rev0378` | `true` |
| `context.timestamp` | `2026.06.18.22.09` | `2026.06.18.22.09` | `true` |
| `context.bundle` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor.zip` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor.zip` | `true` |
| `context.current_revision` | `rev0378` | `rev0378` | `true` |
| `context.current_release` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor` | `true` |
| `context.latest_bundle` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor` | `true` |
| `context.recent_revision_bundle` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor` | `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor` | `true` |
| `context.latest_revision_delta_has_revision` | `True` | `True` | `true` |
| `context.latest_revision_summary_has_revision` | `True` | `True` | `true` |
| `context.summary_has_revision` | `True` | `True` | `true` |
| `receipt.summary_has_revision_delta` | `True` | `True` | `true` |

## Rule

The context pack is a restart artifact. It must not lag behind the manifest or receipt while still passing ordinary generated-surface checks. A freshness pass does not create scientific support; it only prevents stale machine handoff fields from misleading continuation.

