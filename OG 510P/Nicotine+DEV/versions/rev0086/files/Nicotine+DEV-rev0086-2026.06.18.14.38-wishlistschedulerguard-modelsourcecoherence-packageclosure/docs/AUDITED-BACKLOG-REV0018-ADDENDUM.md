# Audited backlog addendum — rev0018

rev0018 audited the transfer-size/opened-file provenance cluster:

```text
U-69  — Peer-controlled transfer-start filesize can expand queued download.
U-107 — Upload sender reads are not clamped to advertised remaining transfer size.
U-198 — Upload authorization/readability checks are path-based and not bound to the opened inode.
```

Result:

```text
verified across 3.3.10, 3.3.x, master
maintainer-style current-behavior witness packaged
public-overlap search refreshed
coherence refactor completed
strict promotions: 0
```

The strongest finding is the combined U-198 + U-107 behavior: a replacement file opened at F init can feed bytes beyond the old advertised size into the upload out buffer because reads are not clamped. This remains audited-backlog rather than strict/front-lane because the opened-file replacement condition is local/sync-race scoped rather than peer-only.

Queue after rev0018:

```text
U-251 — next target: upload EOF/short-read or growing-file lifecycle behavior.
U-244 — possible follow-up: upload queue megabyte limit candidate-size accounting.
U-146/U-159 — lower-priority request-throttle bypass family.
```
