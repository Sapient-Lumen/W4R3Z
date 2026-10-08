# Rematch worlds should store append-only fingerprint catalogs as paged raw-digest blocks

## Claim

Once the archive starts using append-only catalog-slot references for repeat rematch decision packets, the ordered semantic-fingerprint catalog becomes load-bearing state. That catalog should itself be stored as paged raw-digest blocks, not as a growing JSON array of `"sha256:..."` strings.

## Why this is worth keeping

A string catalog is readable, but it wastes durable bytes and makes append locality worse than it needs to be.

Paged raw-digest blocks improve both:

- they store each fingerprint as its 32 raw digest bytes instead of a 71-character string;
- they keep slot order exactly, so existing catalog-slot references still resolve without change;
- and they let append-only maintenance touch only the tail page until it fills, instead of rewriting a full human-readable catalog artifact.

## Operational rule for the inheritor

- Preserve one append-only ordered semantic-fingerprint catalog for long-lived archive objects.
- Store that catalog as page payloads, each carrying a fixed count of raw digests (the family10 toolchain now defaults to `64` per page).
- When you need the human-readable `sha256:` strings, rehydrate them from the paged catalog on demand.
- Append to the tail page until it is full; only then start a new page.
- Keep the page order stable forever, because catalog-slot repeat references depend on those ordinals.

## Executable support

The family10 packet toolchain now includes:

- `fingerprint_catalog_page(...)`
- `expand_fingerprint_catalog_page(...)`
- `fingerprint_catalog_pages(...)`
- `expand_fingerprint_catalog_pages(...)`
- `fingerprint_catalog_lookup_from_pages(...)`
- `append_fingerprint_catalog_pages(...)`

## Measured local result

On the deterministic 274-packet frontier catalog:

- the minified JSON string catalog costs `20277` bytes;
- one monolithic raw-digest page costs `11694` bytes;
- a paged raw-digest catalog at page size `64` costs `11714` bytes;
- so the paged form saves `8563` bytes (`0.422301` share) against the string catalog while preserving exact slot order.

It also improves append locality:

- the current 18-entry tail page is `772` bytes and grows to `814` bytes when one new fingerprint is appended;
- that means one append changes one small page artifact instead of rewriting a `20351`-byte string catalog.

So the next archive rule is not about packet bodies at all. It is about protecting the catalog state that makes slot references possible.
