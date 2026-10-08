# Rev0860 audit

## Question

Why were resume-transfer claim and execution allowed to materialize a complete
persisted source manifest when the planner had already selected the only chunks
that could be acted upon?

## Findings

### 1. Work amplification

Both consumers populated `std::vector<SyncChunkRange>` from every persisted
source chunk, then checked whether the much smaller planned subset appeared in
that vector. This made unrelated manifest rows consume row steps, digest
copies, vector growth, and principal-process memory. It also let malformed
unselected rows veto selected work.

### 2. Namespace authority

The first extracted draft used an unqualified table name. SQLite object-name
resolution searches `temp` before `main`, so a same-name TEMP table on a reused
connection could redirect the proof. The production query and both adjacent
integration evidence queries are now explicitly `main`-qualified. A runtime
regression creates a malicious TEMP shadow and proves that it is ignored.

### 3. Cardinality and duplicate bounds

A point key should be unique in the production schema, but integrity proof must
not assume the constraint it is checking. Each offset query therefore uses
`LIMIT 2`; zero rows rejects absence, one row may authorize after exact checks,
and a second row rejects ambiguity without scanning an attacker-sized duplicate
set.

### 4. Representability and exact decoding

SQLite's integer value domain is signed 64-bit. Both selected offsets and
lengths are rejected during complete preflight when they cannot be represented
exactly. Persisted integers use storage-class-exact decoders; text masquerading
as an integer is rejected. SHA-256 text is copied through a 64-byte ceiling.

### 5. Resource authority

The owner has four independent positive ceilings: complete manifest rows,
selected rows, selected metadata bytes, and selected payload bytes. Metadata
accounts for offset, length, 64-byte digest spelling, and persisted ordinal—88
semantic bytes per selected row. All caller semantics and arithmetic are
checked before the first SQLite data step.

### 6. Lifetime and reuse

One typed statement owns the exact SQLite generation. The owner is final,
noncopyable, and nonmovable. Every normal and exceptional path resets the
statement and clears bindings; missing-row and duplicate-row failures are
followed by successful reuse in the executable corpus.

## Refactor result

The extracted owner is separately compiled and linked into the core. Claim and
execution now consume the same invariant boundary, freeze persisted
`chunk_count`, use planner summaries as limits, and no longer contain a full
manifest vector. CMake registers the focused corpus and source audit. The
release verifier requires the owner, test, and audit for rev0860 and later while
remaining compatible with sealed rev0859.

## Mechanical proof

`tools/audit_sync_sqlite_manifest_chunk_subset.py` passes 63/63 checks. It
locates both integrations and rejects missing main qualification, an unbounded
uniqueness scan, incomplete preflight, non-exact decoding, missing cleanup,
full-manifest vector reintroduction, unbounded adjacent text, absent separate
linkage, or absent package enforcement.

## Remaining exposure

This is not a global persistence-query budget. Other specialized row readers
still require classification. O(K) point probes also assume an attested schema
and suitable lookup index. A future typed query-capability layer should combine
schema identity, index expectation, row-step budget, byte budget, and output
shape in one reusable boundary.
