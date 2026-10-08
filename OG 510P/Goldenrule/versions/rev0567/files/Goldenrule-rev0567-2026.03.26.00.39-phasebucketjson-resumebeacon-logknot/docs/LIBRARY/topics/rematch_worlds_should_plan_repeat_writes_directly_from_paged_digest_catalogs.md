# Rematch worlds should plan repeat writes directly from paged digest catalogs

## Claim

Once the archive already keeps the append-only semantic-fingerprint catalog as paged raw-digest blocks, the live writer should decide repeat-vs-new and emit `short_catalog_reference` / `catalog_reference` packets directly from those pages. Do not rebuild the full ordered JSON list of `"sha256:..."` strings just to answer a write-time repeat question.

## Why this is worth keeping

The previous pass made paged catalogs sufficient for resolving slot references after the fact. That still left a hidden reconstruction tax on the write side:

- the live writer had to expand the ordered fingerprint list before it could tell whether an incoming packet was already present;
- that meant the archive's compact state was not actually sufficient for its own repeat planner;
- and it made the inheritor carry two state surfaces for the same catalog fact.

Direct page-native repeat planning removes that mismatch. The same compact catalog state now supports both:

- read-time slot resolution; and
- write-time repeat detection plus slot-reference emission.

## Operational rule for the inheritor

- Keep the semantic-fingerprint catalog as append-only raw-digest pages.
- For repeat detection, scan those pages directly for the packet's semantic fingerprint.
- If the fingerprint is found and the slot is below `16384`, emit `short_catalog_reference`.
- If the fingerprint is found but the slot is larger, emit `catalog_reference`.
- If the fingerprint is not found, treat the packet as a first write and fall back to the existing zepto first-write chooser.
- Only rebuild the full ordered `sha256:` string catalog for debugging, export, or other human-readable surfaces.

## Executable support

The family10 packet toolchain now includes:

- `find_fingerprint_catalog_slot_from_pages(...)`
- `packet_catalog_reference_write_plan_from_pages(...)`
- `packet_short_catalog_reference_write_plan_from_pages(...)`
- `packet_archive_yocto_write_plan_from_pages(...)`

## Measured local result

On the deterministic 274-packet frontier catalog at page size `64`:

- the page-native yocto planner matches the ordered-catalog yocto planner on all `274 / 274` repeat decisions at the core-field level;
- every current repeat still lands on `short_catalog_reference`;
- average bytes scanned before finding the repeat slot are `7155.124088`;
- that avoids `13121.875912` bytes on average (`0.647131` share) versus rebuilding the full ordered string catalog;
- and it still avoids `4558.875912` bytes on average (`0.389182` share) versus scanning the whole paged catalog list as one expanded object.

So the next archive rule is not another packet codec. It is: use the compact paged catalog state directly for live repeat planning too.
