# rev0081 revision summary

Rev0081 corrects the minimum architecture for `SEARCH-AGAIN-EPOCH-01`.

For ordinary global, room, buddy, and user searches, a best-effort refresh can rekey the existing core request and GUI page to a fresh response token. The executable prototype removes old parser admission and self-search bookkeeping, changes both lookup keys in order, clears generation-owned rows/dedupe/selection state, preserves page/request/view identity, and sends through the existing mode-specific path.

Late old responses are bounded at two stages: unparsed messages lose parser admission, and already-parsed messages cannot find the removed old core key. This restores result-cap capacity without an alias registry, page replacement, or network acknowledgement.

Wishlist is deliberately excluded. Persistent `ignored_users` records seen peers only when an unread results tab is opened. Clearing rows while preserving that history can destroy unread results; clearing history silently performs Reset Seen Results. No wishlist behavior is selected pending explicit product wording and policy.

## Validation

```text
classified research tests:       28/28 pass
source invariants:               32/32 pass
compile checks:                  12/12 pass
baseline upstream units:         60 passed, 1 skipped
patched upstream units:          60 passed, 1 skipped
selected patch:                  none
```

## Cube corrections

Source identity is centralized in `data/current_source_contract.json`. Mutable unit lanes use independent disposable source extractions. All current HOME/XDG/TMP/CWD state lives outside the package, is reduced to a deterministic digest ledger, and is removed. Package validation rejects transient directories in current runtime evidence; a mutation control proves the gate fails closed. Four accidentally rewritten rev0080 evidence files were restored byte-for-byte.

Finalization also removed four duplicate rev0081 narrative files and consolidated their useful content into the authority documents listed by `data/current_revision_contract.json`.
