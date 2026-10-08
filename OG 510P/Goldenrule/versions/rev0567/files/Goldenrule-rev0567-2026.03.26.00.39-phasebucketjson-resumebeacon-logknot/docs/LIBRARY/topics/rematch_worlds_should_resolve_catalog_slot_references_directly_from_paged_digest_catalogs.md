# Rematch worlds should resolve catalog-slot references directly from paged digest catalogs

## Claim

Once the archive already stores the append-only semantic-fingerprint catalog as paged raw-digest blocks, repeat references should resolve directly from those pages. Do not first rebuild a full ordered JSON list of `"sha256:..."` strings unless a human or an export path actually needs that readable form.

## Why this is worth keeping

The short-slot and catalog-slot repeat codecs only pay off if the enabling catalog state stays cheap in practice, not just cheap on disk.

Rehydrating the whole ordered fingerprint list just to resolve one local slot gives back a lot of that win:

- it forces the archive to rebuild a much larger human-readable structure than the repeat reference itself needs;
- it adds avoidable runtime work for the inheritor;
- and it turns a page-local lookup back into a full-catalog expansion step.

Direct page resolution keeps the strong ordered-catalog assumption but removes that reconstruction tax.

## Operational rule for the inheritor

- Keep the ordered semantic-fingerprint catalog as append-only raw-digest pages.
- When a repeat reference is a `short_catalog_reference` or `catalog_reference`, resolve the slot straight from those pages.
- Only rehydrate the full ordered `sha256:` string list for debugging, export, or other human-readable tasks.
- Preserve the fixed page size and stable page order forever, because direct slot resolution relies on the same append-only ordinal contract as the repeat references themselves.

## Executable support

The family10 packet toolchain now includes:

- `fingerprint_catalog_page_entry_count(...)`
- `resolve_fingerprint_catalog_slot_from_pages(...)`
- `resolve_archive_catalog_reference_from_pages(...)`
- `resolve_archive_any_catalog_reference_from_pages(...)`

## Measured local result

On the deterministic 274-packet frontier catalog at page size `64`:

- the full ordered string catalog costs `20277` bytes;
- the full paged digest catalog costs `11714` bytes;
- but direct slot resolution touches only the one target page, averaging `2605.109489` bytes across the current slot distribution;
- that avoids `17671.890511` bytes on average (`0.871524` share) versus rebuilding the full ordered string catalog;
- and it still avoids `9108.890511` bytes on average (`0.777607` share) versus scanning the whole paged catalog.

So the next archive rule is not “invent a new repeat codec.” It is “use the compact catalog state you already kept, directly.”
