# Rev0859 audit

## Question examined

Could a corrupt or attacker-controlled checkpoint force nested manifest
allocation before declared shape, row semantics, aggregate budgets, and stored
identity evidence were accepted? Were duplicate reconstruction paths capable of
drifting in their rejection or commit behavior?

## Findings

### 1. Recorded row counts did not authorize vector growth

Both complete checkpoint entry readers loaded `chunk_count` and `lineage_count`
only as later consistency evidence. Their row loops appended directly to
vectors before the typed validator ran. Rejection therefore followed partial
ownership rather than preceding it.

**Correction:** a single streamed owner admits counts against the rev0858
resource policy before nested growth and rejects the first extra row before a
copy.

### 2. Row semantics were deferred

Chunk contiguity, positive lengths, digest syntax, coverage, lineage identity,
positive counters, uniqueness, and ordering were checked only after complete
materialization.

**Correction:** every property that can be decided from the next row is checked
before its string or object is retained. Exact final counts and file coverage
remain finish-time obligations.

### 3. SQLite text ownership lacked local semantic ceilings

The shared exact-value layer prevented type coercion, but these loaders still
constructed strings without a per-field byte ceiling.

**Correction:** the support layer exposes a bounded exact-text overload. Both
loaders bind every ID, hash, path, and kind copy to the same named limits used
by semantic validation.

### 4. Failure could leave a broad partial value inside the decoder path

The old local vectors lived until stack unwinding and the duplicate peer loader
mutated its broad reconstruction state throughout the query.

**Correction:** ordinary stream failure is sticky and clears the candidate
immediately. The peer loader's caller-owned `SyncManifestEntry` is not touched
until typed validation and both persisted digests agree.

### 5. Validation and decode accounting could diverge

A second hand-written budget calculation in each loader would have recreated a
split authority boundary.

**Correction:** `SyncManifestResourceBudget` is shared, and `finish()` compares
its incremental evidence with independently recomputed typed-validation usage
before commit.

## Refactor shape

- Added a 287-line separately linked decoder owner and 93-line header.
- Added a 442-line, 74-check direct state-machine corpus.
- Added a 415-line, 32-check registered structural audit.
- Replaced two duplicated full-entry row reconstruction loops.
- Added one bounded SQLite text gateway rather than local byte-count logic.
- Changed SHA-256 syntax validation to `std::string_view` without changing
  accepted spelling.
- Added four revision-scoped release-verifier requirements for rev0859 onward.

The active delta is 14 files, 1,614 insertions, and 150 deletions. No bundled
third-party file changed.

## What the audit does not prove

It does not globally bound every wire or persistence decoder. Specialized
chunk-subset readers remain and need purpose-specific row budgets. It does not
isolate hostile SQLite interpretation from the principal process, prove
allocator behavior under process-wide memory exhaustion, establish Windows
runtime behavior, or establish whole-protocol convergence, confidentiality, or
anonymity.
