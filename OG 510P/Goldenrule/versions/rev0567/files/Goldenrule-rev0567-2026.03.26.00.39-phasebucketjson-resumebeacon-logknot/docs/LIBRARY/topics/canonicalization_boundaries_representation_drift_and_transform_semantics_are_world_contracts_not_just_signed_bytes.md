# Canonicalization boundaries, representation drift, and transform semantics are world contracts, not just signed bytes

Stable subject identifiers, portable receipts, and replayable policy are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **which exact representation was protected, which transformations preserve that protection, and which rewrites silently create a different thing**.

- `RS-GR-375` shows that cryptographic operations over JSON need an invariant format, that JCS creates a canonical JSON representation by constraining data to I-JSON and sorting object properties deterministically, and that canonicalization lets systems exchange original JSON on the wire while hashing or signing its canonical counterpart, so future inheritors need the canonicalization boundary itself rather than only the original-looking bytes.
- `RS-GR-376` shows that deterministic CBOR is protocol-specific, forbids indefinite-length items, requires preferred serialization, sorts map keys by bytewise lexicographic order of deterministic encodings, and forces protocols to specify choices around tags and numeric representations, so binary compactness does not remove the need to publish exact serialization semantics.
- `RS-GR-377` shows that DSSE signs the exact serialized body plus a payload type, avoids canonicalization to reduce attack surface, and requires implementations to give the application the same verified bytes that were checked, so one valid design is to publish an envelope contract that freezes bytes and interpretation together instead of canonicalizing document structure.
- `RS-GR-378` shows that RDF Canonicalization defines a stable canonical serialization for RDF datasets, including stable blank-node identifiers across different serializations of the same graph, so some worlds can preserve semantic identity across syntax changes only by declaring a graph-canonicalization layer explicitly.
- `RS-GR-379` shows that current VC Data Integrity guidance treats JCS as attractive for pure JSON, RDF Canonicalization as attractive when JSON-LD semantics must be secured, and warns that proof security depends on canonicalization correctness, so canonicalization choice is part of the security contract rather than a hidden implementation detail.
- `RS-GR-380` shows that Python index-hosted attestations serialize an in-toto JSON statement but treat it as an opaque binary blob on the wire and sign it with DSSE specifically to avoid canonicalization, so production systems already make explicit choices between preserving exact bytes and preserving transformed semantics.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **protected representation layer, canonicalization profile, payload-type binding, or transform-validity semantics** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “has a signature” as the end of the story.

At minimum, it should distinguish between:

1. a world where signatures protect raw bytes only, so harmless whitespace changes, key reordering, or format projection invalidate verification;
2. a world where one syntax gets canonicalized, but payload type, numeric edge cases, or alternate semantic encodings remain underspecified;
3. a world where graph semantics can survive multiple surface syntaxes, but only through an explicitly named canonicalization algorithm with known limits and attack surfaces;
4. a world where an envelope protects exact bytes plus payload type, so transform freedom is intentionally low but replay behavior is crisp;
5. a world where the archive publishes which transformations preserve validity, which require re-signing, and which produce a new derivative subject with its own evidence trail.

These are different worlds.
They change whether future inheritors can safely normalize formatting, port the protected claim across JSON / YAML / CBOR / JSON-LD projections, or know that any representational rewrite created a different verification object even when human meaning looked unchanged.

So canonicalization boundaries, representation drift, and transform semantics belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact protected representation layer for each proof: raw bytes, canonical JSON, deterministic CBOR, canonical RDF dataset, or opaque envelope bytes;
2. the payload type, schema identifier, or semantic contract bound to the protected representation;
3. which transformations preserve validity: whitespace changes, key ordering, field-order normalization, graph-syntax conversion, tag normalization, or none;
4. the exact canonicalization / deterministic-encoding profile in force, including number handling, map-key ordering, tag rules, blank-node handling, or other profile-specific constraints;
5. whether verifiers return the exact verified bytes / canonical form to applications or may reparse and rewrite data after verification;
6. how transformed derivatives are related to the original subject: same protected object, signed alias, derived artifact, or entirely new subject requiring new receipts.

Without that compact contract, future inheritors can mistake representation drift for Golden-Rule progress.
