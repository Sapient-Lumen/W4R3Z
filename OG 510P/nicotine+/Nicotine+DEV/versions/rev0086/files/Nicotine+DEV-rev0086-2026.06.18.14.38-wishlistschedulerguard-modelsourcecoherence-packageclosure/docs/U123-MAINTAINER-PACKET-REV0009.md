# U-123 maintainer packet — rev0009

rev0009 converts U-123 from a local audit proof into a maintainer-usable package:

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py
report_drafts/U123-maintainer-report-skeleton.md
evidence/rev0009-u123-maintainer-source-trace.md
evidence/rev0009-u123-maintainer-reproducer-run.txt
evidence/rev0009-u123-probe-rerun.jsonl
```

## What changed from rev0008

rev0008 established the socket/F-connection consequence. rev0009 packages it into a single `unittest`-style current-behavior reproducer that can be run against an upstream source tree without network sockets.

The reproducer passed as a current-behavior proof on all archived source lanes:

```text
github-tag-3.3.10: OK
github-branch-3.3.x: OK
github-branch-master: OK
```

## What the reproducer asserts today

```text
1. first queued download accepts peer token 4242;
2. second queued download from the same claimed username also accepts token 4242;
3. active_users[username][4242] is overwritten from first to second;
4. FileTransferInit for token 4242 attaches an F socket/file handle to second;
5. firing first.request_timer_id causes _transfer_timeout(first) -> _deactivate_transfer(first);
6. _deactivate_transfer(first) deletes active_users[username][4242] even though it points at second;
7. progress and close callbacks for second are ignored;
8. second remains Transferring with the file handle still open in the probe.
```

## How to convert into a fixed-behavior regression

After a patch, invert the central assertions:

```text
- duplicate same-user/same-token activation should be rejected/quarantined, OR replacement should cleanly deactivate the old transfer first;
- _deactivate_transfer(first) must not remove active_users[username][token] when the mapped object is second;
- progress/close for the second F socket must still be processed or the socket/session must be actively closed.
```

## Why both fix pieces matter

A duplicate activation guard alone prevents the shown path, but an identity-checked `_deactivate_transfer()` is still needed as a stale-callback defense. An identity check alone prevents the stale timer from deleting the later mapping, but still allows a duplicate token to overwrite the first active transfer. A coherent fix should do both.
