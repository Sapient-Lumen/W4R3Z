# PB-01 artifact coherence refactor — rev0074

## Problem

PB-01 accumulated historical witnesses, “selected” patches, production-gate prose, clean-room exports, copied tests, and patch-stack derivatives. Their filenames preserved old confidence while the current cube had no authoritative packet-status map. A reader could open a valid historical artifact and mistake it for a current recommendation.

The active tests also duplicated nearly the same fake network fixture in two 16–17 KB modules. That made policy roles hard to see and encouraged interpreting “all fixed tests pass” as evidence that the desired policy was correct.

## Refactor

The active PB-01 surface now has one shared harness and four role-specific tests:

```text
pb01_harness.py
  common fake sockets, selector, message framing, and source import

test_pb01_current_behavior_witness.py
  two observations of current source; not desired-policy assertions

test_pb01_race_compatibility_controls.py
  behavior that an experiment must preserve

test_pb01_rev0038_split_counterexample.py
  a negative policy test exposing the old blanket guard

test_pb01_origin_aware_experiment.py
  three assertions for a narrower, still-unselected hypothesis
```

The prior active bytes are preserved under `docs/archive/rev0073-active-pb01/`.

## Measured change

```text
archived original test pair: 2 files, 924 lines, 33,838 bytes
active harness plus tests:    5 files, 436 lines, 12,870 bytes
line reduction:               488 lines (52.8%)
byte reduction:               20,968 bytes (62.0%)
explicit test roles:          4
```

The file count rises because roles are separated; implementation duplication falls because the harness is centralized. This is a meaningful reduction, unlike a minification or line-packing exercise.

The broader PB-01-classified inventory contains 331 files or references across the historical cube. The current audit classifies 38 as superseded-policy experiments and 29 as duplicate handoff exports. It finds 23 exact duplicate hash groups totaling 121,621 bytes beyond one canonical copy. Those bytes are retained where provenance or old manifests depend on them; the correction is to remove them from the active decision path, not to erase history indiscriminately.

## Status coherence

Rev0074 adds `data/current_packet_dispositions.json`. Current landing pages point to it, and `tools/audit_rev0074_packet_status.py` fails if:

- PB-01A gains a non-null selected patch;
- PB-01B is not retired as a defect on current evidence;
- an active landing page reasserts the old production-gated decision;
- a current status marker is missing from the report-draft archive;
- generated inventories change when the audit is rerun without source changes.

Historical files are not rewritten. They are classified in `data/rev0074_pb01_artifact_inventory.csv` as historical evidence, superseded experiment, archived original, or duplicate export. Current status must be read from the ledger and rev0074 disposition.

## Severe correction

The severe error was epistemic, not syntactic: the cube had converted a synthetic state transition into a production recommendation without closing network reachability or compatibility intent. More test infrastructure then reinforced the chosen policy. Rev0074 corrects the decision and the artifact topology together.
