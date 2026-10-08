# Evidence budget and retention roadmap — rev0068

## Decision

The linked cloudtainer is a working research object, not the permanent home of every raw transition ever generated. Historical evidence must remain verifiable, but it should not be copied into every revision.

## Measured baseline

The uploaded rev0067 archive contains:

```text
files:                                  1,959
uncompressed size:                     939.300 MiB
bulk transition/segment evidence:      717.707 MiB
replay JSONL traces:                    62.362 MiB
exact duplicate redundancy:             2.309 MiB
compiled build artifacts:               0.256 MiB
```

Bulk transition/segment evidence plus replay traces account for 83.05% of uncompressed bytes. Exact duplicate cleanup is therefore secondary.

## Retention classes

### Core-linked

Keep in every linked revision:

```text
source and C++ source
tests and current audit scripts
current executable specification
manifest, revision log, environment record, checksums
claim registry and question registry
compact aggregate/summary data
small claim-relevant transition samples
small replay samples
raw-evidence index
```

### Evidence-archive

Store once, content-addressed:

```text
full *_cpp_transitions.csv
full segment tables
full replay JSONL
large historical game/payoff tables when compact summaries exist
```

Every object must record:

```text
sha256
bytes and row count
MIME/schema
source revision
producing script and command
input seed family
compact derivative(s)
claim(s) that depend on it
storage URI or bundle path
```

### Generated-disposable

Never ship by default:

```text
build/
__pycache__/
.pytest_cache/
*.pyc
local shared objects and executables
```

## Safe migration algorithm

1. Select one revision family, starting with the largest old raw transition table.
2. Hash the original file and record bytes/rows/schema.
3. Confirm a reproducer command and compact derivative exist.
4. Compress or move the original into an immutable evidence bundle.
5. Add the content address and bundle location to the core index.
6. Run all tests, inherited audits, package contract, and a dependency scan for the old path.
7. Remove the raw file from the linked core only after the index and evidence bundle verify.
8. Never rewrite an already published evidence object's bytes under the same identifier.

## Practical first migration tranche

Start with rev0033–rev0042 full transition tables. They contain several of the largest files and are not the current claim frontier. Preserve compact summaries, models, docs, and small samples in core. Keep rev0064–rev0067 claim-relevant replay and compact samples linked until the current claim registry stabilizes.

## Budget targets

```text
next linked core:       < 300 MiB uncompressed
mature linked core:     < 150 MiB uncompressed
new raw full traces:      0 in core unless explicitly justified
unindexed evidence:       0 bytes
build/cache artifacts:    0 files
```

The size target is subordinate to evidence integrity. Missing provenance is worse than a large cube; indexed immutable evidence is better than repeated ballast.
