# Rematch Worlds Should Store Digest-Byte Route Blocks Beside Paged Catalogs

## Claim

When the archive already stores append-only paged raw-digest fingerprint catalogs, it should keep a small digest-byte route-block sidecar beside them so repeat lookup can jump straight to candidate pages instead of linearly scanning every page-filter artifact first.

## Why

Page filters already proved that the archive can answer repeat queries from compact paged state. The remaining waste was not wrong decisions, but linear filter scanning: every repeat lookup touched many filter artifacts that could only say “not here.” Route blocks compile the same first-byte evidence into a direct page map, so the live writer only touches one small route block and the candidate pages it actually needs to inspect.

## Local Result

On the current deterministic 274-packet frontier with the live `16`-entry compact page default:

- average repeat lookup falls from `1467.306569` bytes with page filters to `1101.153285` bytes with route blocks,
- while compact state rises only from `12653` bytes to `12891` bytes,
- so the route-block sidecar buys `366.153285` bytes of average lookup reduction for only `238` more bytes of compact state, without changing any repeat decisions.

## Implementor Rule

- If the archive only has paged raw-digest catalogs, use direct page-native lookup.
- If it also has page filters, use filtered page-native lookup.
- If it also has digest-byte route blocks, treat those as the top repeat-planning sidecar because they preserve the same repeat decisions while skipping linear filter scans.
- Keep route blocks archive-local; they are an optimization over compact state, not an export format.

## Append Locality

Route blocks are aligned to the page catalog and grouped by the high nibble of the first digest byte. Under normal append-to-tail growth, one newly appended fingerprint only changes the single route block corresponding to its first-byte group, so the archive does not have to rewrite the whole sidecar just to record one new semantic object.
