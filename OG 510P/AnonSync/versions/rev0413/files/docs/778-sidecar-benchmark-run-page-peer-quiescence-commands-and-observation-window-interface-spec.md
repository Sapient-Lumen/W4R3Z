# Sidecar benchmark run page — peer quiescence, commands, and observation window interface spec

## Purpose

A sidecar benchmark run is not just a pasted command sequence.
It is an externally executed experiment whose meaning depends on quiescence truth, role assignment, direction coverage, and preserved outputs.

AnonSync should therefore model execution as a reviewed **sidecar benchmark run page** instead of hiding it behind support prose.

## Core decision

The run page must answer:

1. which peers are participating
2. whether the required quiescence really happened
3. which subtests actually ran, in what order
4. what outputs were captured
5. whether the run is trustworthy enough to compare back to Sync

## Required sections

1. **Preflight and quiescence**
2. **Run ledger**
3. **Command / action rows**
4. **Observed outputs**
5. **Validity and anomaly review**
6. **Return-to-product handoff**

## 1) Preflight and quiescence

Show before any test row begins:

- peer roles (`server`, `client`, `reverse witness`, etc.)
- intended endpoint / port basis
- Sync state on each peer (`confirmed stopped`, `quiet but not stopped`, `unknown`)
- competing traffic warning
- environment notes that narrow interpretation

The page must plainly distinguish `requested to stop Sync` from `confirmed stopped`.

## 2) Run ledger

Maintain a durable ledger with one row per subtest.
Each row should preserve:

- row id
- transport family
- direction
- start and end time
- operator / peer that initiated it
- status (`planned`, `running`, `completed`, `invalid`, `aborted`)
- short outcome summary

## 3) Command / action rows

The page may generate exact command text or helper actions, but each row must also preserve:

- why this row exists
- the prerequisite quiescence claim
- what output counts as success
- what failure invalidates comparison
- whether a retry is allowed without resetting the experiment

Commands are subordinate to the experiment object, not the other way around.

## 4) Observed outputs

For each completed row, preserve:

- throughput / latency / loss summary as applicable
- stdout or parsed result attachment
- notable warnings
- direction-specific anomalies
- confidence tag

The page should not flatten forward and reverse results into one optimistic average.

## 5) Validity and anomaly review

Before the run is accepted, review at least:

- missing directions
- partial matrix coverage
- quiescence failure
- endpoint mismatch
- obvious competing traffic
- stale endpoint or wrong port usage
- output parse failure

A benchmark with broken isolation should remain visible as a failed or weakened experiment, not silently disappear.

## 6) Return-to-product handoff

The run page should hand back:

- the best supported raw network ceiling band
- any asymmetry finding
- whether the result can be compared to the earlier baseline
- what question remains unanswered
- the next allowed page (`performance hypothesis review`, rerun, or abort)

## Compact rendering obligations

Any compact benchmark summary must preserve:

- participant pair
- quiescence verdict
- matrix coverage
- strongest supported ceiling statement
- invalidity reason if any

## Anti-clone rule

Do not clone support flows that dump four shell commands into an article and leave the operator to remember which ones actually ran or whether Sync was truly stopped.
AnonSync should preserve quiescence proof, run rows, outputs, and validity verdict in one durable execution object.
