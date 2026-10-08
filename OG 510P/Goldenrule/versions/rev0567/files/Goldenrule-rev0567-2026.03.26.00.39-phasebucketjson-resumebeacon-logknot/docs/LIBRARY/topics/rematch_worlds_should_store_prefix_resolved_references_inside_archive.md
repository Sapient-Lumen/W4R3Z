# Rematch worlds should store prefix-resolved references inside the archive

Once a rematch decision already has a long-lived body in the archive, the next duplicate write is no longer a body problem. It is an address problem.

The portable reference packet was the right first step because it made deduplication explicit and kept exported packets self-contained. But inside the archive, that portable form still pays to restate a full `sha256:` fingerprint string on every repeat write even though the archive already maintains the content-addressed body index that can resolve a shorter local pointer.

That means the in-archive repeat contract should split from the export contract:

- outside the archive, keep the full portable fingerprint reference;
- inside the archive, use the shortest unique local fingerprint prefix that resolves against the known semantic-body index;
- and keep the full fingerprint only in the index, not in every repeat artifact.

For the current family10 packet layer, a `12`-hex prefix floor is already enough across the representative semantic decisions tested on `2026-03-07`, so repeat references can shrink materially without giving up deterministic resolution.

The implementor rule is simple: first write a semantic core for a new fingerprint, then on later repeats write only an archive-local prefix reference unless the packet is leaving the archive boundary.
