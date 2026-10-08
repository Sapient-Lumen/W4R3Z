# rev0044 public-overlap notes — U-138 ID3v2 boundary

## Sources checked

- ID3v2.3.0 public specification context: ID3v2 stores metadata in frames; v2.3 frames use an identifier, size, flags, and payload.
- ID3v2.4 structure context: tag size is encoded as a 32-bit synchsafe integer with 28 effective bits, allowing a large advertised tag body.
- Nicotine+ public issue adjacency around share scanning duration/performance problems, especially historical issue reports about rescanning taking many hours.

## Public-overlap classification

```text
protocol/spec adjacency: yes
Nicotine+ share-scan performance adjacency: yes
direct public duplicate of U-138 share-scanner mapped-ID3v2-frame materialization: not captured
rev0044 strict-front classification: not promoted
```

## Why this matters

The public specifications make clear that ID3v2 can carry large tagged metadata bodies. However, rev0044's source/probe work shows that the broad U-138 formulation was over-wide for Nicotine+'s MP3 share-scanner duration-only route: that route skips the ID3v2 payload before duration scanning.

The remaining tag-enabled TinyTag behavior is recorded as parser hardening backlog, not as a production-gated Nicotine+ share-scanner packet.
