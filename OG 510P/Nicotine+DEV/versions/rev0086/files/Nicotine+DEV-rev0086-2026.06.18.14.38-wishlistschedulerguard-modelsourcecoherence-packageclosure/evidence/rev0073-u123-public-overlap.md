# U-123 targeted public-overlap note — 2026-06-17

## Search boundary

Targeted searches covered the Nicotine+ issue and pull-request namespace using combinations of:

```text
duplicate transfer token
same-user token collision
active_users token transfer
queued transfer token
transfer token replacement
```

No result found in this pass described the complete U-123 chain:

```text
same username + reused peer-supplied transfer token
-> active transfer owner replaced
-> stale first cleanup removes later owner's slot
-> later progress/close lookup is orphaned
```

This is a bounded search result, not a universal novelty claim.

## Adjacent public context

Nicotine+ issue #653, “Transfer connection initiation following an unallowed (queued) transfer response,” concerns queued/disallowed response sequencing and subsequent transfer connection behavior. It is transfer-lifecycle adjacency, but its reported trigger and state chain differ from U-123.

Nicotine+ issue #2978, “Connection closed and other connectivity problems,” reports downloads that can ignore retry/pause behavior after connection failures. It is symptom adjacency only; the issue does not identify duplicate peer tokens or active-map ownership replacement.

## Current interpretation

```text
exact direct overlap found: no, within the captured targeted searches
adjacent transfer-lifecycle reports: yes
novelty proved: no
routing effect: none by itself; impact evidence remains decisive
```

Public sources observed:

```text
https://github.com/nicotine-plus/nicotine-plus/issues/653
https://github.com/nicotine-plus/nicotine-plus/issues/2978
```
