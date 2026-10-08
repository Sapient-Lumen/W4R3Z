# rev0036 U-123 public-overlap note

Search date: rev0036 session.

## Sources checked

```text
Nicotine+ Soulseek Protocol documentation
https://nicotine-plus.org/doc/SLSKPROTOCOL.html

Nicotine+ issue #653 — transfer connection initiation following an unallowed/queued transfer response
https://github.com/nicotine-plus/nicotine-plus/issues/653

Nicotine+ issue #2978 — connection closed and connectivity problems
https://github.com/nicotine-plus/nicotine-plus/issues/2978

Nicotine+ issue #2926 — downloads stuck on queued
https://github.com/nicotine-plus/nicotine-plus/issues/2926

Soulseek.NET issue #668 — UploadDenied / transfer cleanup adjacency
https://github.com/jpdillingham/Soulseek.NET/issues/668
```

## Classification

```text
candidate no exact direct public match found; transfer-lifecycle adjacent public issues exist
```

The protocol documentation confirms the token linkage between `TransferRequest` and `FileTransferInit`. The public issues show transfer-lifecycle and symptom adjacency: queued/unallowed response timing, connection closed/timeouts, stuck queued transfers, and cleanup after `UploadDenied`. They do not appear to duplicate the narrower rev0036 U-123 chain: duplicate peer-supplied download token, stale first timeout, active-map deletion, and ignored later F-connection progress/close callbacks.

## Conservative wording for report draft

Do not say that the broader transfer lifecycle has no public history. Say instead:

```text
I did not find a direct public duplicate for this same-user/same-token stale-timeout active-map identity chain. Related transfer-lifecycle and queue/connection symptoms have been discussed publicly.
```
