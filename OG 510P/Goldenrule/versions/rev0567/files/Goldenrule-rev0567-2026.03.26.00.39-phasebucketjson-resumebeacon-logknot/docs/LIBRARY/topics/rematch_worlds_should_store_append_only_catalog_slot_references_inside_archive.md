# Rematch worlds should store append-only catalog slot references inside the archive

## Claim

Once the archive already deduplicates rematch decision packets by semantic fingerprint, repeat writes should stop storing prefix-based local references whenever the archive can preserve an append-only ordered fingerprint catalog. In that setting, the repeat artifact should store the local catalog slot instead of a fingerprint prefix.

## Why this is worth keeping

Prefix references are self-locating, but they keep paying for hash material on every repeat write. A catalog slot pays only for a small local ordinal. That makes repeats smaller and resolution cheaper:

- smaller, because the stored repeat artifact only carries one tag byte plus a uvarint slot index;
- simpler, because the resolver can do one direct catalog lookup instead of scanning for a unique prefix match;
- stable enough for archive-local use, as long as the catalog is append-only and slot ids are never recycled.

## Operational rule for the inheritor

- Keep one append-only ordered list of semantic fingerprints for long-lived archive objects.
- Never renumber or recycle an existing slot.
- For a repeat write inside that archive, store a `catalog_reference`.
- If the archive state is available only as an unordered fingerprint set, fall back to the older `byte_reference` form.
- For export outside the archive, keep using the portable full-fingerprint reference path.

## Executable support

The family10 packet toolchain now includes:

- `ordered_fingerprint_catalog(...)`
- `packet_catalog_reference(...)`
- `expand_catalog_reference_packet(...)`
- `resolve_archive_catalog_reference(...)`
- `packet_archive_yocto_write_plan(...)`

## Measured local result

On the deterministic 274-packet family10 frontier catalog:

- prefix byteframe repeats cost `3288` total minified bytes (`12` each);
- catalog-slot repeats cost `1516` total minified bytes (`5` bytes for the first `128`, `6` bytes for the remaining `146`);
- total savings are `1772` bytes (`0.538929` share).

So the next storage rule is not another semantic codec. It is a stronger archive-state assumption: if the archive is willing to preserve append-only fingerprint ordinals, repeat writes can shrink again.
