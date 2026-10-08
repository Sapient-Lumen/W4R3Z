# Semantic survival, schema pinning, and vocabulary continuity are world contracts, not just verified bytes

Verified bytes, stable subject identifiers, and declared protected representations are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what the verified statement meant once media types, predicate vocabularies, schema dialects, contexts, or version markers drift or disappear**.

- `RS-GR-381` shows that media types are registered format identifiers used across protocols, so long-horizon interpretation begins with a durable type label rather than a filename, endpoint, or parser guess.
- `RS-GR-382` shows that JSON Schema dialects are sets of vocabularies and semantics and that `$schema` declares the dialect in force, so even familiar keywords do not keep a stable meaning unless the dialect and vocabulary contract are preserved.
- `RS-GR-383` shows that JSON-LD meaning depends on `@context`, that `@version` exists to stop older processors from producing different output, and that remote contexts may be fetched automatically, so linked-data semantics can silently depend on external interpretation documents unless they are pinned.
- `RS-GR-384` shows that the current in-toto statement layer uses `_type` and `predicateType` to identify which statement and predicate schema are in play, so an attestation's truth conditions depend on retained predicate semantics rather than on a valid signature over generic JSON alone.
- `RS-GR-385` shows that the current SCITT architecture expects statements to be tagged with a relevant media type to help interpretation, so receipts prove registration but do not make unlabeled or ambiguously typed content self-explanatory.
- `RS-GR-386` shows that SPDX's `specVersion` is the reference needed to parse and interpret an element across future changes, so version markers are first-class meaning-preservation evidence rather than cosmetic metadata.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **media-type tagging, predicate/schema identity, schema dialect, context pinning, vocabulary continuity, or unknown-term handling** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “the bytes still verify” as the end of the story.

At minimum, it should distinguish between:

1. a world where bytes verify but no durable media type, predicate type, schema dialect, or version marker survives beside them;
2. a world where type labels survive, but schemas, contexts, or vocabularies are still resolved live from remote locations;
3. a world where a schema version survives, but custom vocabularies, extension registries, or unknown-term behavior remain implementation folklore;
4. a world where the archive retains the interpretation bundle locally — media type, statement / predicate type, schema dialect, profile, context, and extension rules — and fails closed on unknown semantics;
5. a world where future inheritors can replay both old and new semantic rulebooks and see that the bytes stayed the same while the meaning contract changed.

These are different worlds.
They change whether future inheritors can merely verify that some bytes were once accepted, reconstruct what claim vocabulary those bytes expressed, or detect that a later parser / schema / context upgrade silently changed the meaning of an apparently stable statement.

So semantic survival, schema pinning, and vocabulary continuity belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact interpretation identifiers bound to each verified statement: media type, statement type, predicate type, schema ID, dialect, profile, and version marker;
2. which schemas, contexts, vocabularies, and extension registries are embedded, mirrored locally, hash-pinned, or still resolved live;
3. how unknown fields, unknown terms, unknown vocabularies, or unsupported extensions are handled: ignore, warn, reject, quarantine, or operator review;
4. whether semantics come from a standards document, a profile bundle, an implementation convention, or a live registry lookup;
5. whether the archive preserves enough local interpretation material for fully offline meaning reconstruction and not just offline signature checking;
6. how semantic upgrades, deprecations, or profile supersessions are related to older receipts so future inheritors can distinguish byte stability from meaning drift.

Without that compact contract, future inheritors can mistake semantic drift for Golden-Rule progress.
