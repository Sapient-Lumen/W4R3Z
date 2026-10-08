# U-123 coherence/refactor audit — rev0037

## Refactor finding

Rev0036 grouped U-123 around stale timeout/deactivation. Rev0037 splits that packet into two related but distinct invariants:

| invariant | purpose | final disposition |
|---|---|---|
| active-owner collision rejection | do not allow a second same-user/same-token download request to replace a different active F-connection owner | required production fix gate |
| identity-aware deactivation | do not let stale cleanup for object A delete a slot now owned by object B | defensive hardening; necessary if duplicate activation is ever allowed |

This refactor prevents a misleading promotion of the identity-only patch. The identity-only patch passes the rev0036 narrow stale-timeout regression, but it fails the rev0037 active-owner collision regression.

## Boundaries retained

- This is not PB-01 peer primary-election/generation binding. PB-01 is about selecting the correct P-connection/session identity. U-123 is about the transfer active map and F-connection callbacks after a peer-supplied transfer token is accepted.
- This is not SEARCH-RESP-01 search response source/scope validation. SEARCH-RESP-01 is parser/acceptance ordering for search results. U-123 is transfer-session state ownership.
- This is not U-138 media-parser materialization. No local file parser budget is involved.
- This is not general upload queue policy. The selected regression is download-side handling of a peer-supplied `TransferRequest` token.

## Queue effect

U-123 remains rank #1 but now has a production-gated maintainer packet. PB-01 becomes the next strict/front work item after a final human filing review of U-123.
