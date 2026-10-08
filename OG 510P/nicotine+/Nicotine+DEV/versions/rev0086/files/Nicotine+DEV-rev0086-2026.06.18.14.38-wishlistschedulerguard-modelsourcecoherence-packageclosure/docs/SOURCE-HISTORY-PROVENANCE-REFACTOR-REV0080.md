# Source-history provenance refactor — rev0080

## Failure mode

The cube had strong current-source invariants but no current machine authority for *how the behavior arrived*. That allowed rev0078–rev0079 to analyze queue architecture deeply while underweighting two decisive historical facts:

```text
Search Again originally coexisted with a manual result reset
that reset was later removed by an otherwise unrelated wishlist overhaul
```

Current-file-only analysis could correctly describe every function and still miss the cross-commit regression.

## Refactor

Rev0080 adds:

```text
data/current_source_history_contract.json
tools/audit_current_source_history.py
data/rev0080_source_history_summary.json
data/rev0080_source_history_checks.csv
evidence/rev0080-source-history-provenance.md
```

The JSON contract owns commit identities and predicates. The Python engine is revision-neutral and supports:

```text
ancestor relationships
exact commit subjects
file contains at a commit
file does not contain at a commit
```

The tool discovers the external source ZIP by content hash, safely extracts its `git-full/` tree to a temporary directory, and evaluates the contract with Git. Historical source is not embedded in the cube.

## Validated chain

```text
d8ffe30c…  preparation refactor
    ↓
9fddad99…  same-token Search Again + Clear All Results
    ↓
91296257…  wishlist overhaul removes Clear All Results
    ↓
f4e17d59…  bundled executable head retains the interaction
```

All 15 history claims and 36 total contract/transport/history checks pass.

## Self-audit correction

The first implementation retained every `git show` output as a runtime log. Because several predicates inspected the same historical `search.py` snapshot, this created about 682 KiB of duplicated source text. The final tool records only command, return code, output byte count, and output SHA-256:

```text
initial source-history runtime: ~682 KiB
final compact command ledger:   2,886 bytes
embedded historical source:     none
```

The predicate results remain in `data/rev0080_source_history_checks.csv`; full source stays in the external content-addressed bundle.

## Active-evidence compaction

The former open-first `search-epoch-01` artifact is retained unchanged as historical evidence for the optional in-place branch:

```text
13 files / 2,011 lines / 73,774 bytes
```

The new open-first `search-repeat-01` artifact is:

```text
7 files / 382 lines / 15,693 bytes
```

Current authority therefore drops 6 files, 1,629 lines, and 58,081 bytes while preserving the prior models outside the current navigation surface. This is authority compaction, not deletion of reproducibility evidence.
