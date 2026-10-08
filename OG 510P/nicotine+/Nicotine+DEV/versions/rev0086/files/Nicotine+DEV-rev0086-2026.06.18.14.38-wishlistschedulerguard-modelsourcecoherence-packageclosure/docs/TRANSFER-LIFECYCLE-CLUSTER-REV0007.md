# rev0007 transfer lifecycle coherence/refactor

## Purpose

This is the requested higher-order check: some individually reasonable fixes become incoherent when combined. rev0007 applies that check to the transfer lifecycle cluster rather than creating more registry rows.

## Result

U-123 is now the concrete anchor for **TR-01a active transfer map integrity**. It should be solved together with U-169/U-170 because they all rely on whether `username + token` identifies a live transfer session strongly enough.

U-158/U-166 stay nearby but separate. They are username/path status-message provenance issues; a duplicate-token guard does not fix them because the relevant protocol messages do not carry the transfer token.

U-269 stays separate. It concerns successful upload completion and connection lifetime after bytes are sent, not transfer-token collision before an F connection starts.

U-270 and the search-response parser/lifetime family remain high priority but should be handled in a separate parser-ordering pass. Mixing them into the transfer-token changeset would hide the key proof and create an oversized unfocused report.

See `data/rev0007_transfer_lifecycle_coherence.csv` for the machine-readable refactor.

## Change combinations that are coherent

```text
Duplicate activation guard
+ identity-checked deactivation
+ FileTransferInit expected-session check
= coherent TR-01a transfer-session integrity change.
```

This combination directly addresses the rev0007 proof. It also avoids leaving stale timers able to delete a different transfer object.

## Change combinations to avoid

```text
Duplicate activation guard only
```

This is incomplete if stale timers/cancels can still remove the wrong map entry.

```text
Global token uniqueness across all users
```

This risks breaking compatibility because transfer tokens are scoped by peer/session behavior, not a global namespace.

```text
Token-binding claims for UploadDenied/UploadFailed
```

This is incoherent unless the protocol is extended, because those status messages are not token-bearing in the current message shape.
