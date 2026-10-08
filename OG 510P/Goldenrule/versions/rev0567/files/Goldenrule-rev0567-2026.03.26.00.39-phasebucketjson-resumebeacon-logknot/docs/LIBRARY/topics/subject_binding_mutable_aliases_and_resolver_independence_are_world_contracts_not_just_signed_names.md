# Subject binding, mutable aliases, and resolver independence are world contracts, not just signed names

Portable receipts, replayable policy, and archived status history are still not enough for any successor-facing archive if future inheritors cannot also tell **what exact subject those materials were about once names, tags, URLs, or hosting locations have moved**.

- `RS-GR-369` shows that `ni` names identify digital objects by hash, separate naming from later dereferencing, and compare names by digest algorithm and value rather than by auxiliary URI fields, so the core subject identifier can survive location or resolver changes.
- `RS-GR-370` shows that in-toto subjects must carry digests, are assumed to be immutable, and are matched purely by digest even when `name` or `uri` fields are present, so attestations should bind to immutable subject identity rather than to mutable presentation labels.
- `RS-GR-371` shows that Docker digests are immutable while tags can be reused or changed, and that one displayed multi-platform tag can stand for an index plus several platform-specific digests, so human-facing names and variant resolution are separate contracts from object identity.
- `RS-GR-372` shows that OCI registries define digests as unique identifiers, tags as human-readable pointers, and referrers as subject relationships to a specified digest, so signatures, SBOMs, and attestations are most safely correlated to immutable subject digests rather than to whichever tag happened to resolve at inspection time.
- `RS-GR-373` shows that SWHIDs are identifiers rather than URLs, embed intrinsic cryptographic object identifiers, separate context qualifiers from the core identifier, and can be computed before archival, so resolver-independent subject continuity can coexist with preserved contextual lineage.
- `RS-GR-374` shows that cosign signatures protect object digests and that tag-to-digest mappings, when important, should be separately signed as annotations, so mutable alias bindings are their own evidence surface rather than an implied side effect of object signing.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **subject identity model, alias mutability, variant-resolution semantics, digest pinning, or resolver independence** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat a signed tag, URL, filename, or repository path as a complete subject contract.

At minimum, it should distinguish between:

1. a world where proofs mention only mutable names, URLs, or tags;
2. a world with immutable digests somewhere in the system, but without retaining which aliases pointed to which digest at decision time;
3. a world where attestations bind to digests, but later status, supersession, or attachment material is still looked up by mutable names;
4. a world where immutable subject identifiers are primary and alias-to-subject mappings are separately signed, logged, or archived;
5. a world where immutable subject identifiers remain replayable without live resolver trust, while contextual qualifiers preserve how that subject was located, packaged, or socially named at the time.

These are different worlds.
They change whether future inheritors can merely re-ask a still-live service what a name means, reconstruct which exact artifact an old proof covered after tags moved, or preserve both the core object identity and the historically relevant alias / context without confusing one for the other.

So subject binding, mutable aliases, and resolver independence belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact immutable subject identifier retained for each protected artifact: digest, `ni` URI, SWHID, or another declared intrinsic identifier;
2. which fields are only mutable aliases or discovery handles: filenames, tags, URLs, package coordinates, registry paths, or branch / release labels;
3. whether attestations, receipts, signatures, status records, supersession records, and referrers correlate by immutable subject identifier or by mutable name;
4. how multi-variant or multi-platform names resolve, and whether each concrete variant gets its own immutable subject identifier;
5. whether alias-to-subject mappings are themselves signed, logged, timestamped, or otherwise retained as first-class evidence;
6. whether future inheritors can verify subject identity without live resolver trust, and if not, which resolver or lookup dependency remains in the trust base.

Without that compact contract, future inheritors can mistake alias drift or resolver survival for Golden-Rule progress.
