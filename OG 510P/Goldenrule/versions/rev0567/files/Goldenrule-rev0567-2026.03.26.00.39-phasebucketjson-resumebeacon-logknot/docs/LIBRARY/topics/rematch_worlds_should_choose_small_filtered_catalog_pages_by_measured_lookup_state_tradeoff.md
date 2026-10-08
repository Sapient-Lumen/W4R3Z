# Rematch worlds should choose small filtered catalog pages by measured lookup/state tradeoff

## Claim

Once the archive keeps semantic-fingerprint catalogs as filtered paged raw-digest blocks, it should stop inheriting `64`-entry pages by default. The page size should be chosen by the measured tradeoff between compact-state bytes and average filtered repeat-lookup cost. Under the current family10 deterministic frontier, the right clean default is `16` entries per page.

## Why this is worth keeping

Earlier passes made repeat reads and repeat writes run directly against the compact paged catalog state. That changed what the page size controls:

- smaller pages do not just change catalog serialization;
- they change how many raw-digest bytes the archive has to touch for the common repeat path; and
- once aligned digest-byte filters exist, the old `64`-entry page size is no longer a neutral default.

The measured frontier shows that:

- `8`-entry pages produce the smallest average filtered repeat lookup in the clean power-of-two candidate set;
- but `16`-entry pages achieve nearly the same lookup cost with much less sidecar overhead and fewer page artifacts;
- and `16` is the best power-of-two page size under the combined objective `full_compact_state_bytes + average_repeat_lookup_bytes_with_filters`.

So the archive should now prefer `16`-entry filtered pages instead of carrying `64` forward as an inherited constant.

## Operational rule for the inheritor

- Keep filtered paged raw-digest catalogs.
- Default to `16` entries per page for that filtered catalog state.
- Treat `64`-entry pages as the old baseline, not the live default.
- Re-open the page-size frontier only if the archive’s fingerprint population or lookup/write mix changes materially.
- Keep the compact repeat rules unchanged: direct page-native repeat detection, direct page-native slot resolution, and `short_catalog_reference` whenever the resolved slot remains below `16384`.

## Executable support

The family10 packet toolchain now encodes the new default directly:

- `DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE = 16`
- `FILTERED_FINGERPRINT_CATALOG_PAGE_SIZE_CANDIDATES = (8, 16, 32, 64, 128)`

The new measured snapshot is:

- `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_size_snapshot_20260307.{md,json}`

## Measured local result

On the deterministic `274`-packet frontier catalog with aligned digest-byte filters:

- `64`-entry pages cost `11960` compact-state bytes and `3850.540146` average filtered repeat-lookup bytes;
- `16`-entry pages cost `12653` compact-state bytes and `1467.306569` average filtered repeat-lookup bytes;
- so moving from `64` to `16` adds only `693` compact-state bytes but saves `2383.233577` lookup bytes on average (`0.618935` share);
- `8`-entry pages push average lookup a little lower to `1379.390511`, but they raise compact state to `13571` bytes and lose the cleaner joint objective.

So the next archive rule is not a new packet form. It is: once repeat planning and repeat resolution already live inside filtered compact catalogs, use smaller filtered pages and make `16` the default clean power-of-two size.
