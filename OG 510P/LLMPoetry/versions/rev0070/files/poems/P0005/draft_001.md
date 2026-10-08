# All Three Bits Said Yes

## Poem

INSERTED
CASE-0017
CASE-0021
CASE-0028

QUERY
CASE-1001

BIT 17 | SET BY CASE-0021
BIT 28 | SET BY CASE-0017
BIT 26 | SET BY CASE-0028

FILTER
POSSIBLY PRESENT

EXACT SET
NOT PRESENT

All three bits said yes.
No record did.

## Disclosure

Disclosure: P0005-D001 / rev0070 is a machine-drafted Bloom-filter poem backed by the deterministic artifact at `poems/P0005/artifact/d001`. The exact ledger contains only `CASE-0017`, `CASE-0021`, and `CASE-0028`. The absent query `CASE-1001` maps to bits 17, 28, and 26. Those bits are all set, but each was set by a different inserted record; the filter therefore answers `POSSIBLY PRESENT` although the exact set proves the query was never inserted.

The artifact uses a 32-bit insertion-only filter and three domain-separated SHA-256 probes. It commits the four-byte filter, exact input ledger, query, rendered surface, spec, and receipt. `tools/check_bloom_false_positive_poem.py` independently recomputes every probe and bit, proves no false negative for the inserted records, proves this exact false positive, verifies one distinct owner per query bit, and rebuilds the artifact byte-for-byte in a temporary directory.

The source pressure is bounded. Bloom's 1970 paper introduced hash coding with allowable errors. NIST's later analysis describes Bloom filters as probabilistic membership structures: a non-member may coincidentally map only to already-set bits, producing a false positive; for small filters, predicted false-positive rates require particular care. This poem claims no rate and represents no real person, case, database, screening system, or adverse action. No current/live membership status is claimed.

P0005-D001 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, and not a reader response. P0002-D010 remains the first external disclosed-reader target with zero logged responses. P0003-D004 and P0004-D002 remain byte-frozen internal candidates.
