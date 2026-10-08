# Cloudtainer triage — rev0091

## Current state

The archive is healthy enough to work on: validation passes, manifest checking works, and the project has a clear narrow-waist design. The main risk is not chaos; it is accumulated ceremony around a compact idea.

## Corrected in this revision

```text
Duplicate semantic vector IDs: fixed
JSON Schema date-time assertion: enabled
Post-evaluation observation reuse: rejected
Per-input max_age_seconds: enforced
```

## Waste or drift to correct over time

### 1. The validator is too large

`tools/validate_archive.py` is over 3,300 lines. It is already split by functions, but responsibilities still share one file: schema loading, profile digest rules, transport checks, evidence summaries, lifecycle authority, replay transparency, discovery negotiation, scope composition, and manifest checking. This makes regressions more likely because unrelated edits happen in the same module.

Suggested path:

```text
tools/validation/schema_contract.py
tools/validation/digest_contract.py
tools/validation/temporal.py
tools/validation/profile_catalog.py
tools/validation/discovery.py
tools/validation/replay_transparency.py
tools/validation/aggregate_lifecycle.py
tools/validation/scope_composition.py
```

### 2. Digest canonicalization overpromises

The spec now names RFC 8785/JCS for current-use canonical JSON surfaces, but the executable digest helper still uses Python `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)`. That is deterministic for the in-corpus objects, but it is not a full JCS implementation. The next revision should either add a real JCS canonicalizer or constrain digestable inputs so numbers, Unicode edge cases, duplicate keys, and I-JSON limits cannot create cross-implementation digest drift.

### 3. Temporal coherence is still local to scope composition

rev0090 and rev0091 harden `scope-composition-guard`, but the same timestamp-window idea appears in aggregate correction authority lifecycle checks, replay-transparency anchor evaluation, policy lifecycle references, discovery downgrade proof metadata, and notification observations. Those should share one temporal module rather than growing separate timestamp idioms.

### 4. Fixtures are copied, not generated

The archive has hundreds of JSON fixtures, especially negative fixtures. This is good for review, but wasteful for turn-by-turn cloudtainer work. A later revision should keep canonical rendered fixtures while generating them from smaller base objects and patch files. That would make one-line semantic mutations obvious and reduce accidental duplicate examples.

### 5. Historical archive material is useful but should be tiered

`archive/original-rev0060` is valuable research history, but it is not needed for every validation loop. A future distribution could keep a full research bundle and a slim current bundle. The slim bundle should retain manifests and migration maps, but omit deep historical notes unless explicitly requested.

## Speculative direction

TimeSync is strongest as a semantic envelope around existing time mechanisms, not as another time protocol. The design pressure from NTPv5, NTS, PTP, Roughtime, UTC-transition planning, and signed/transparency-oriented ecosystems points toward a narrow TimeState plus explicit evidence surfaces. The risk is letting evidence surfaces quietly become provenance, certification, or actionability. The archive has mostly resisted that; the remaining work is to make those boundaries smaller, executable, and easier to audit.
