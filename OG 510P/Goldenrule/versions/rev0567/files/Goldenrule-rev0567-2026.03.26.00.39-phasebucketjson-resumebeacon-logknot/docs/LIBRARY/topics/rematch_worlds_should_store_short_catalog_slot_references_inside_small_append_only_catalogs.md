# Rematch worlds should store short catalog-slot references inside small append-only catalogs

## Claim

Once the archive already preserves an append-only ordered semantic-fingerprint catalog, the common repeat case under a modest catalog size should not pay a full tag-plus-uvarint slot wrapper. When the local catalog slot fits below `16384`, the repeat object should store a `short_catalog_reference` that packs the slot into one 14-bit short token.

## Why this is worth keeping

The generic catalog-slot reference already made repeats much smaller than prefix byteframes, but it still grows from `5` to `6` minified bytes once the slot crosses `127` because the uvarint adds a second payload byte.

The archive now has a stronger fact available:

- the local catalog is append-only and ordered;
- the current frontier catalog is only `274` entries long;
- and many future sessions will still live far below `16384` entries.

So a fixed-width short-slot token is cheaper than a tag-plus-uvarint wrapper across that whole range.

## Operational rule for the inheritor

- Preserve one append-only ordered semantic-fingerprint catalog for long-lived archive objects.
- For repeat writes against that catalog, prefer `short_catalog_reference` when the slot is below `16384` and the archive preserves the short-slot decoder.
- Fall back to the older `catalog_reference` when the ordered catalog is larger than the short-slot range.
- Fall back again to `byte_reference` when only an unordered fingerprint set is available.
- Keep the slot order stable forever, because both short and generic catalog references depend on those ordinals.

## Executable support

The family10 packet toolchain now includes:

- `packet_short_catalog_reference(...)`
- `expand_short_catalog_reference_packet(...)`
- `packet_short_catalog_reference_write_plan(...)`
- updated `packet_archive_yocto_write_plan(...)` logic that prefers the short form when the ordered catalog slot fits

## Measured local result

On the deterministic 274-packet frontier catalog:

- prefix byteframe repeats cost `3288` total minified bytes;
- generic catalog-slot references cost `1516` bytes;
- short catalog-slot references cost `1370` bytes;
- so the short form saves another `146` bytes (`0.096306` share) against generic catalog-slot references and `1918` bytes (`0.583333` share) against prefix byteframes.

The practical effect is simple:

- generic catalog references cost `5` bytes for slots `0`-`127` and `6` bytes for slots `128`-`16383`;
- short catalog references stay at `5` bytes across that whole current range.

That is only a one-byte improvement per upper-half repeat, but it is a genuine durable win and it keeps the archive’s top repeat rule aligned with the stronger ordered-catalog assumption it already accepted.
