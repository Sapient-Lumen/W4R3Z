# rev0012 coherence refactor — transfer status provenance

rev0012 intentionally reduces overlap. The goal is not to turn every related handler into a separate report.

## New family map

| Family | Rows | Decision |
|---|---|---|
| TR-01 transfer token/lifecycle | U-123 lead, U-169/U-170 context | Keep U-123 strict and separate. |
| PB-01 peer connection election/source binding | U-168 + U-176 lead, U-165 context | Keep PB-01 strict and separate. |
| TR-STATUS-01 transfer status-message provenance | U-158 lead, U-166 support | Audited hardening, not strict standalone in rev0012. |
| SEARCH-RESP-01 search response token/source/scope | U-163 next, U-262/U-267 support | Next substantive batch. |

## Why U-158 is not just U-123

U-123 is a transfer-token collision and stale-timeout/F-session orphaning problem. U-158 is status-message authority: `UploadFailed` and `UploadDenied` carry a filename/path, but not a transfer token or generation. The handlers then apply side effects based on claimed username and virtual path.

They should not be merged because a fix for one does not necessarily fix the other.

## Why U-158 is not just PB-01

PB-01 is peer connection primary election and source binding. U-158 becomes more adversarial when PB-01-like source misbinding lets the wrong connection claim the target username. However, U-158's handler-level state transitions are download-transfer specific and should become regression tests for a complete provenance fix.

They should be cross-linked, not collapsed.

## Why U-166 is demoted

U-166 has a real current-behavior witness, but the effect is queue-position mutation. Without a stronger downstream consequence, it is a low-value UI/state hardening subcase. Keep it as a regression companion for pending request-generation binding; do not present it as a separate security report.

## Next queue rationale

The next high-risk incomplete family is SEARCH-RESP-01:

```text
U-163 lead: FileSearchResponse acceptance is token-only and not bound to requested source/scope.
U-262 support: private result lists parsed before private-search-results display policy.
U-267 support: invalid-token early drop may still decompress peer-controlled prefix fields.
```

This should be probed as one coherent search-response batch, not as three separate reports at the outset.
