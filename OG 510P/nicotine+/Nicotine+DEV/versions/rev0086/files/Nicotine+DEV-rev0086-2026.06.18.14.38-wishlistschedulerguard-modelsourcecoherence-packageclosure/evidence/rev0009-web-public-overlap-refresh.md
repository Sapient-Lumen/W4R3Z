# rev0009 web/public overlap refresh

This pass prioritized public-overlap checking for the items touched in rev0009, rather than trying to re-search all 274 rows.

## U-123 — duplicate peer-supplied download transfer token / stale timeout / F-session orphaning

Targeted public searches used exact or near-exact terms:

```text
site:github.com/Nicotine-Plus/nicotine-plus "duplicate" "transfer token"
site:github.com/Nicotine-Plus/nicotine-plus "TransferRequest" "token" "duplicate"
site:github.com/Nicotine-Plus/nicotine-plus "active_users" "token" "transfer"
site:github.com/Nicotine-Plus/nicotine-plus "FileTransferInit" "active_users"
```

Result: no direct public report was found for the full invariant now proven locally:

```text
same-user duplicate TransferRequest token -> second F socket attaches -> stale first timeout deletes second active-map entry -> progress/close callbacks are ignored -> second session/file handle remains open in the probe
```

Still public-adjacent:

- Nicotine+ issue #653 discusses transfer connection initiation around queued/disallowed transfer responses and includes transfer-token/connection sequencing context.
- Nicotine+ issue #2978 discusses connection-closed/stuck transfer symptoms, but does not directly describe duplicate peer-supplied TransferRequest tokens.
- Release notes for 3.3.11 RC include broad spoofed-user upload and network-message hardening, so novelty remains "candidate no direct public match found," not proven-new.

## U-269 — completed upload remains active after advertised bytes are sent until peer closes F socket

Targeted public searches used:

```text
site:github.com/Nicotine-Plus/nicotine-plus/issues upload connection remains open after transfer complete socket open Nicotine+
site:github.com/Nicotine-Plus/nicotine-plus/issues "Upload" "socket" "complete" "Nicotine+"
"completed upload connections" "Nicotine+"
"all bytes are sent" "Nicotine+" upload socket
"file-upload-progress" "UploadFile" "Nicotine+"
```

Result: public material is too adjacent to call U-269 a clean-new strict item. The rev0009 local probe confirms the source behavior, but public symptom/history exists around upload completion/progress/connection behavior.

Adjacent public material captured:

- Issue #2447: uploads listed as 100% complete on uploader side while reportedly aborted at 99% on downloader side; also mentions uploads jumping to 100% then later requeueing.
- Issue #3173: slow/dropping upload behavior; not a direct post-advertised-size connection lifetime proof.
- Reddit /r/Soulseek thread: users stuck on Transferring at 0 bytes; a comment says Nicotine+ 3.2.5/3.2.6 fixed related stuck upload issues.
- Issue #2978: connection-closed/stuck transfer symptoms.

rev0009 classification: U-269 is source-confirmed and reproducible at handler level, but remains an audited-backlog candidate, not strict. It should be framed as a small upload-lifecycle hardening/regression test: after the upload sender has queued/sent the advertised final byte, the app should either finish locally or actively close/retire the F socket/session, not depend only on peer close plus eventual idle cleanup.

## U-270 — FileSearchResponse trailing partial data keeps peer connection open

Public-overlap result: demote from clean-fresh strict path to public-adjacent/backlog. The release notes contain historical search/socket overlap:

```text
Open a new socket for every outgoing search result to avoid problems with shared sockets getting closed.
Only close sockets of incoming search results if input/output buffers are empty. (this may still result in the transmitting sockets)
```

That language is old and not necessarily the exact current U-270 invariant, but it is direct enough to prevent any "previously unmentioned" claim until a new current-source proof establishes a narrower residual problem.

## URLs captured

- https://github.com/nicotine-plus/nicotine-plus/issues/653
- https://github.com/nicotine-plus/nicotine-plus/issues/2978
- https://github.com/nicotine-plus/nicotine-plus/issues/2447
- https://github.com/nicotine-plus/nicotine-plus/issues/3173
- https://www.reddit.com/r/Soulseek/comments/xujmfw/started_on_nicotine_on_upload_some_users_stuck_on/
- https://nicotine-plus.org/NEWS.html
- https://nicotine-plus.org/doc/SLSKPROTOCOL.html
