# STORAGE-RETENTION.md note — rev0106

Rev0106 adds the evaluation-verdict gate and metadata coherence hardening; historical content follows.

---

# Storage and retention policy — rev0040

## Problem

The cube stores history mainly by copying revision-named JSON, dashboards, and large probe outputs into every package. This preserves context but obscures freshness and makes growth roughly cumulative.

Baseline rev0039 measurements found:

- 3,934 files and about 246.5 MB unpacked;
- 3,069 files (about 204.1 MB) in revision-named logical families;
- about 68.8 MB of normalized-JSON duplication after revision/timestamp fields are ignored;
- 95 of 101 current-revision probe JSONs normalized-identical to an earlier revision;
- no run command/code/environment provenance in the 101 current-revision probe JSONs inspected.

These are audit estimates, not a claim that every repeated byte is dispensable.

## Target layout

```text
objects/sha256/<prefix>/<hash>       immutable raw/derived objects
runs/<run-id>/run.json               command, code/input/env hashes, seeds, timings
revisions/rev####/manifest.json      pointers plus decisions, not copied payloads
latest/                              convenience pointers generated from manifests
```

A derived report must name its input object hashes and transformation tool hash. Scientific raw output is immutable.

## Retention tiers

- **Hot:** source, ledgers, current decisions, current run manifests, small summaries.
- **Warm:** unique raw outputs and reports referenced by active lanes.
- **Cold:** superseded but unique historical objects; optional external bundle.
- **Drop:** exact duplicates, bytecode/cache debris, and current-revision aliases with no execution or derivation event.

## Migration

1. rev0040: stop manufacturing current-revision scientific aliases; add quarantine and measurements.
2. rev0041: emit run manifests and content hashes for one repaired lane.
3. rev0042: convert the largest revision families to object references while retaining an export tool.
4. rev0043: make thin packages the default and ship a separate optional historical-object bundle.
