# Rematch worlds should store digest-byte page filters beside paged catalogs

## Claim

Once the archive already keeps the append-only semantic-fingerprint catalog as paged raw-digest blocks, it should also keep one tiny digest-byte page filter beside each page and use those filters before scanning page digests for repeat detection. Do not linearly decode every raw-digest page on every repeat lookup when a much smaller sidecar can rule most pages out first.

## Why this is worth keeping

The previous pass made compact paged catalogs sufficient for both:

- read-time slot resolution; and
- write-time repeat detection plus slot-reference emission.

That still left a meaningful scan tax:

- repeat lookups had to read page-sized raw-digest payloads until they reached the page holding the target slot;
- non-repeat lookups still paid page scans even though most pages were impossible matches;
- and the archive had no tiny sidecar for saying "this page definitely does not contain a digest whose first byte is `x`".

A per-page first-byte membership mask is small enough to keep in the archive without fighting the size budget, but strong enough to skip most pages before touching their 32-byte digests.

## Operational rule for the inheritor

- Keep the semantic-fingerprint catalog as append-only raw-digest pages.
- Keep one aligned page filter beside each page.
- Build each filter as a 256-bit membership mask over the first digest byte values present on that page, plus the page entry count.
- For repeat detection, scan the page filters first and only decode a raw-digest page if its filter says the target first byte might be present.
- If the filtered lookup finds a slot below `16384`, emit `short_catalog_reference`.
- If it finds a larger slot, emit `catalog_reference`.
- If it finds no slot, fall back to the existing zepto first-write chooser.
- When appending a new fingerprint, update only the tail page filter unless the append opens a new page.

## Executable support

The family10 packet toolchain now includes:

- `fingerprint_catalog_page_filter(...)`
- `fingerprint_catalog_page_filters(...)`
- `fingerprint_catalog_page_filter_might_contain(...)`
- `append_fingerprint_catalog_page_filters(...)`
- `find_fingerprint_catalog_slot_from_pages_with_filters(...)`
- `packet_archive_yocto_write_plan_from_pages_with_filters(...)`

## Measured local result

On the deterministic 274-packet frontier catalog at page size `64`:

- aligned page filters cost only `246` total minified bytes (`48` per page);
- full compact state rises from `11714` paged-catalog bytes to `11960` bytes when those filters are included;
- filtered repeat planning still matches unfiltered page-native planning on all `274 / 274` repeat decisions at the core-field level;
- every current repeat still lands on `short_catalog_reference`;
- average repeat lookup cost drops from `7155.124088` bytes to `3850.540146` bytes;
- that saves `3304.583942` bytes on average (`0.461849` share) versus unfiltered page-native scans;
- and the tail filter remains `48` bytes before and after a one-fingerprint append, so the sidecar keeps the same append-locality story as the paged catalog itself.

So the next archive rule is not a new packet body. It is: keep tiny digest-byte page filters beside the compact catalog pages and let them prune repeat lookups before any raw-digest scan begins.
