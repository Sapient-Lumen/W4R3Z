# rev0068 patch semantic coherence refactor

rev0068 refactors the archived-source patch evidence stack by separating semantic/minimality review from the adjacent proof layers.

## Separation map

```text
source intake / safe extraction (rev0064)
  proves the uploaded source bundle is safe to consume.

Git provenance / tree match (rev0065)
  proves extracted source lanes match bundled Git provenance.

hunk preimage binding (rev0066)
  proves split patches match source preimages and expected file scopes.

fixture contract / test hygiene (rev0067)
  proves exported clean-room tests and patches are copied from intended artifacts and avoid cube-private dependencies.

patch semantic/minimality gate (rev0068)
  proves the split patches contain only expected semantic edit classes and required invariant markers.
```

## De-overmerge decisions

The following rows remain deliberately distinct:

```text
U-123 transfer-session identity:
  active download collision rejection and identity-aware deactivation.

PB-01 peer primary election:
  established primary preservation and safe secondary behavior.

SEARCH-RESP source admission:
  direct-user, buddy, and room request-source binding in search.py.

SEARCH-RESP parser budgets:
  compressed username-prefix and accepted public/private result-count limits in slskmessages.py.

Public path traversal/watch:
  public PR context only, not a new private strict/front packet.
```

## Why this refactor was needed

Prior gates already proved that patches apply, tests pass, and clean-room exports are portable. Those gates did not produce a compact reviewer-facing semantic inventory of the patch lines themselves. rev0068 fills that gap by classifying add/delete lines and checking for broad-scope drift such as new imports, dynamic execution helpers, config/UI changes, or network-message-ID changes.

## Result

The semantic/minimality audit found:

```text
semantic inventory rows: 470
forbidden semantic findings: 0
file-scope rows: 12/12 pass
marker-contract rows: 48/48 pass
source touched-file rows: 15/15 pass
negative controls: 5/5 pass
```

The strict/front packet set stays frozen at seven production-gated packets.
