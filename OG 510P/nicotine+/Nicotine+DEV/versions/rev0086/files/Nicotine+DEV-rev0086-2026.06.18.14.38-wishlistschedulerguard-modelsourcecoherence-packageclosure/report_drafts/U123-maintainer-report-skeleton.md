# U-123 maintainer report skeleton — duplicate peer-supplied download transfer token can orphan a later F-connection session

**Status in cube:** strict report-candidate, not production-ready disclosure text.  
**Affected source lanes checked:** 3.3.10 tag, 3.3.x branch snapshot, master branch snapshot from the rev0003 source bundle.  
**Impact boundary:** peer-driven transfer-session integrity / availability. Not code execution. Not standalone file disclosure.

## Summary

When handling peer-supplied `TransferRequest(direction=UPLOAD)` messages for queued downloads, Nicotine+ accepts the peer-supplied token and stores the active transfer under `active_users[username][token]`. A second queued download from the same claimed username can reuse the same token and overwrite the active-map entry for the first transfer. If the first transfer's stale request timer later fires, `_deactivate_transfer(first)` deletes the shared `username+token` active-map entry without checking that the mapped object is still `first`. A later `FileTransferInit`, progress, or close callback for the second transfer then has no active-map entry to find.

rev0008/rev0009 local probes show the concrete consequence: the second transfer can enter `Transferring`, attach an F socket and local incomplete-file handle, then be removed from the active lookup by the stale first timeout. Subsequent progress and close callbacks for the second socket are ignored, leaving the second session/file handle open in the probe.

## Minimal reproduction shape

See:

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py
```

The reproducer uses no network sockets. It creates two queued downloads for the same username, accepts two peer-supplied `TransferRequest` messages with the same token, attaches an F connection to the second transfer, fires the first transfer timeout, then confirms that progress and close callbacks for the second transfer are ignored.

The reproducer passed against all three source lanes in rev0009:

```text
github-tag-3.3.10: OK
github-branch-3.3.x: OK
github-branch-master: OK
```

## Root-cause invariants

```text
Transfers._activate_transfer(): active_users[username][token] = transfer, no duplicate guard.
Transfers._deactivate_transfer(): deletes active_users[username][token] without checking mapped object identity.
Downloads._file_transfer_init(), _file_download_progress(), and _file_connection_closed(): all depend on active_users[username][token].
```

## Suggested fix shape

A minimal coherent fix should do both of these, not just one:

```text
1. Reject/quarantine a second active TransferRequest for the same username+token unless it refers to the same transfer generation.
2. Make _deactivate_transfer() identity-checked: only delete active_users[username][token] when the current mapped object is the same transfer being deactivated.
```

The second step protects against other stale callbacks/timers even if a duplicate activation path is missed. The first step prevents the bad state from being created in the normal download request path.

## Regression acceptance criteria

A fixed-behavior unit test should assert:

```text
- after first TransferRequest, token maps to first transfer;
- after duplicate-token second TransferRequest, either the second request is rejected/quarantined OR the old first transfer is cleanly deactivated before replacement;
- firing the stale first timeout must not remove the active mapping for the second transfer;
- progress/close callbacks for the second F socket must still be processed or the socket must be actively closed;
- distinct-token control still works.
```

## Public-overlap wording

Public transfer-lifecycle material exists, especially around queued/disallowed transfer connection initiation and stuck/closed transfer symptoms. In rev0009 hard searches, no direct public report was found for the full duplicate peer-supplied `TransferRequest` token plus stale timeout plus F-session orphaning invariant. Phrase novelty as:

```text
candidate no direct public match found in targeted search
```

not as:

```text
new vulnerability / never reported
```
