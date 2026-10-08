# Cloudtainer maintenance policy — rev0057

## Problem

The cube is scientifically careful but operationally overweight. It ships source, summaries, docs, historical raw evidence, replay traces, compiled outputs, Python caches, and pytest caches in one layer.

The current rev0057 size audit records:

```text
total files: 1700
total uncompressed size: 916.742 MiB
raw transition CSV count: 34
raw transition CSV bytes: 718221428
cache/build file count: 139
cache/build bytes: 2168796
```

## Policy

Use three artifact tiers.

### Tier 1 — linked working cube

Keep:

```text
README.md
manifest.json
CHECKSUMS.json
src/
tests/
scripts/
cpp source files
docs/
compact data summaries
claim cards
small CSV aggregates
```

### Tier 2 — raw evidence archive

Move or compress:

```text
*_cpp_transitions.csv
*_replay_traces.jsonl
large historical payoff/game CSVs when compact summaries exist
```

Preferred storage form:

```text
data/raw/rev####/*.csv.gz
data/raw/rev####/*.jsonl.gz
```

Every raw archive must have a small summary row in Tier 1 containing row count, hash, source script, and reproduction command.

### Tier 3 — never integrity-track by default

Do not ship or checksum unless a revision is specifically about build artifacts:

```text
__pycache__/
.pytest_cache/
build/*.so
build/muc5_*
```

## Migration plan

1. Add this policy and the size audit first.
2. In the next housekeeping revision, introduce `.mucignore` or an explicit checksum include-list.
3. Compress old transition CSVs after confirming summary hashes.
4. Keep the latest claim-relevant raw traces accessible until the claim card is accepted.
5. Run tests, smoke, audit, and checksum after pruning.

## Caution

This policy is not permission to erase evidence. It is a plan to separate reproducible proof from convenience caches and oversized working files.

