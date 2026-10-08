# Publish dry-run public edge

`publishdryrun.py` models a no-network staging boundary after bridge shadow, audit quorum, and redress GC.

A dry-run attempt binds:

- public channel: mutable head, garden catalog, seed portfolio, or public bridge record;
- profile, service, scope, request, subject, and payload digests;
- bridge-shadow, audit-quorum, redress-GC, and optional transport-shadow digests;
- sequence and previous-attempt memory;
- family and path-family hints.

This catches the bug class where every component passed, but not for the same object, request, payload, channel, sequence, or local-memory boundary.

A component accepted-with-watch can stage a watched dry run only when policy permits.  Component quarantine blocks staging.
