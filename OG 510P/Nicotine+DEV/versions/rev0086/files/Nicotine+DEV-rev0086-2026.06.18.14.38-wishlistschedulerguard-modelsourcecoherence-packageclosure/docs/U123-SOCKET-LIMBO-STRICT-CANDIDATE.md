# rev0008 U-123 strict-candidate report notes

## One-sentence summary

A peer can reuse the same `TransferRequest` token for two queued downloads under the same claimed username; after the second transfer reaches the F-connection stage, the stale timeout from the first transfer can delete the second transfer's active-map entry, causing later progress and close callbacks for the second socket/file session to be ignored.

## Why rev0008 changed the status

rev0007 proved the handler/timer overwrite. rev0008 adds the missing socket/F-connection consequence. The second transfer is no longer merely in `Getting status`; it reaches `Transferring`, has an F socket and local incomplete-file handle, and then becomes unindexed after the stale first timer fires.

See:

- `evidence/rev0008-u123-socket-limbo-probe.md`
- `evidence/rev0008-u123-socket-limbo-probe.jsonl`
- `evidence/rev0008-u123-source-trace.md`

## Evidence matrix

| lane | duplicate requests accepted | second F socket attached | stale first timeout deleted second active mapping | progress ignored afterward | close ignored / handle open afterward |
|---|---:|---:|---:|---:|---:|
| github-tag-3.3.10 | True | True | True | True | True |
| github-branch-3.3.x | True | True | True | True | True |
| github-branch-master | True | True | True | True | True |

## Impact boundary

This is an availability and transfer-session integrity issue. It is not a remote code execution claim and does not itself prove file disclosure. The practical risk is stuck/orphaned download state, ignored progress/close cleanup for a live file socket, and potential slot/resource confusion under malicious or malfunctioning peer behavior.

## Public overlap and novelty wording

Use this exact class until stronger evidence appears:

```text
candidate no direct public match found; public transfer-lifecycle adjacent
```

Public issue #653 discusses transfer connection initiation after an unallowed/queued transfer response. Soulseek.NET #668 discusses odd transfer cleanup around `UploadDenied`. These are adjacent enough that we should not say nobody has ever hit related transfer lifecycle bugs. The rev0008 invariant is narrower: duplicate peer-supplied download token, stale first timeout, active-map deletion, and ignored F-connection progress/close callbacks.

## Coherent report structure

Recommended single report title:

```text
Duplicate peer-supplied download transfer tokens can orphan an active F-connection transfer session
```

Recommended report shape:

1. Explain protocol context: TransferRequest carries the token; FileTransferInit reuses it on an F connection.
2. Show source invariant: activation overwrites by username+token; deactivation deletes by username+token without object identity; progress/close use same lookup.
3. Show local proof matrix across 3.3.10, 3.3.x, master.
4. Bound severity to availability/transfer state.
5. Suggest duplicate activation guard plus identity-checked deactivation plus expected-session checks.

## Not included in the same report

- U-158 and U-166 are not token-bearing paths and should not be forced into this fix.
- U-269 is a different phase: upload completion after bytes are sent.
- U-270 is a search-response parser/lifetime issue, not transfer-session state.
