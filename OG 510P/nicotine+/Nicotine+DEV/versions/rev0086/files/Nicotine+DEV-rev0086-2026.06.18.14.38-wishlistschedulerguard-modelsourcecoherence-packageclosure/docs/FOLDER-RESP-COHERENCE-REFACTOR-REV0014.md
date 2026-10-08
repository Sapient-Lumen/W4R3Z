# FOLDER-RESP coherence refactor (rev0014)

rev0014 deliberately avoids turning one folder-response root into four separate reports.

## Canonical grouping

| Row | rev0014 role | decision |
|---|---|---|
| U-167 | FOLDER-RESP-01 canonical audited-backlog lead | Source/test confirmed; not strict-promoted. |
| U-255 | parser materialization support/regression | Covered by FOLDER-RESP-01 tests; not standalone. |
| U-260 | stale/nonmatching-response control-flow support | Covered by FOLDER-RESP-01 tests; public folder-download bug adjacency; not standalone. |
| U-268 | prefix decompression/allocation support | Covered by FOLDER-RESP-01 tests; master partially mitigates with allowed-response gating; not standalone. |
| U-256 | separate FolderContentsRequest request-to-response echo/budget family | Keep separate from response-token binding. |
| U-272 | duplicate/alias of U-256 | Never standalone. |

## Coherence warnings

- Do not propose a token-only fix that removes or bypasses master/future `AddAllowedResponse` source/folder gating.
- Do not consume the pending request on an otherwise malformed or wrong-token response.
- Do not break legacy latin-1 fallback by treating all empty responses as terminal failures.
- Do not solve U-255 only with a larger uncompressed-size cap; the semantic problem is materializing irrelevant returned folders before the requested-folder filter.
- Do not merge U-256 into U-167: request echo/budget hardening and response token/generation binding have different code paths and regression tests.

## Presentation decision

FOLDER-RESP-01 is useful for the audited backlog and maintainers' regression suite. It is not currently a fourth front-lane item because the strict document should remain reserved for cleaner, higher-impact, less publicly-overlapped invariants.
