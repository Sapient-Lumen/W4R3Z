# Release-candidate state and open-item freeze

The archive can be lint-clean and still have one honest external-data dependency. This surface makes
that state explicit so the archive does not oscillate between false closure and endless internal
work.

The rule is: **ship a ready-but-not-closed archive only when the remaining item is externally gated,
clearly named, and protected by validators that prevent fake closure**.

## Release candidate states

| Code | Meaning | Release posture |
|---|---|---|
| `RC0` | draft changes not linted | Do not package. |
| `RC1` | lint clean, but live queue not reconciled | Package only for internal review. |
| `RC2` | live queue reconciled; external gate named | Package with explicit live-item warning. |
| `RC3` | negative fixtures and no-fake-import guards pass | Package as ready-but-not-closed. |
| `RC4` | public summary, surface map, context pack, and release manifest are synchronized | Package as next usable revision. |
| `RC5` | real import closure-ready after `SRC2+` acceptance | Eligible to close `FT-0181`. |
| `RCX` | validator failure, fake closure, or protected leakage | Do not package. |

## Open-item freeze rule

A live followthrough item may remain open in a packaged revision when all are true:

1. it is blocked by unavailable external evidence, not by known internal drafting work;
2. the block is named in `FOLLOWTHROUGH_QUEUE.json` and `REVISION_RECEIPT.json`;
3. validators prevent examples, templates, readiness manifests, or acceptance packets from being
   misread as real evidence;
4. the package contains an explicit next evidence request or acceptance path;
5. the release does not claim the live item is closed.

This rule currently applies to `FT-0181` only.

## Release candidate JSON contract

Release-candidate records live in `examples/release-candidates/`. They declare revision, state,
allowed-to-ship posture, open followthrough ids, externally gated ids, required lint checks,
no-fake-import assertion, unresolved blocks, next unblocker, and last reviewed date.

`tools/check_release_candidate_state.py` verifies that the release-candidate record matches the
actual queue and receipt. It fails if a package claims to ship with open items that are not named as
external gates.

## What does not count as progress

These do not justify another internal branch by themselves:

- adding another realistic service record while still lacking `SRC2+` evidence;
- adding more public-summary prose without a new redaction failure;
- adding schema fields not supported by decision-delta evidence;
- adding more control-plane files after the invariant, dependency graph, delta, recovery-drill, and
  closure-checklist layers unless they catch a new failure mode;
- repeating the no-real-data statement without adding a new acceptance, rejection, request, release
  control, handoff control, lifecycle decision, closeout control, invariant, graph, drill, or
  closure-checklist control.

## Current archive bet

A good late-stage archive can distinguish “unfinished because we lack evidence” from “unfinished
because we have not designed the workflow.” rev0222 is intended to be the former: internally ready,
open about the missing real import, handed off explicitly, control-covered, refresh-scheduled,
quorum-bound, invariant-bound, graph-visible, drill-ready, closure-checklist explicit, and guarded
against fake closure.

See [`real-pilot-record-import-and-normalization-workflow.md`](real-pilot-record-import-and-normalization-workflow.md),
[`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md),
[`import-negative-fixtures-and-failure-mode-catalog.md`](import-negative-fixtures-and-failure-mode-catalog.md),
[`operator-handoff-and-maintainer-runbook.md`](operator-handoff-and-maintainer-runbook.md),
[`service-lifecycle-deprecation-and-archive-exit-rules.md`](service-lifecycle-deprecation-and-archive-exit-rules.md),
[`real-import-closeout-board-and-decision-minutes.md`](real-import-closeout-board-and-decision-minutes.md),
[`control-coverage-matrix-and-validator-trace.md`](control-coverage-matrix-and-validator-trace.md),
[`evidence-refresh-calendar-and-staleness-gates.md`](evidence-refresh-calendar-and-staleness-gates.md),
[`human-signoff-quorum-and-conflict-attestation.md`](human-signoff-quorum-and-conflict-attestation.md),
[`release-invariants-and-claim-boundaries.md`](release-invariants-and-claim-boundaries.md),
[`artifact-dependency-graph-and-control-plane.md`](artifact-dependency-graph-and-control-plane.md),
[`version-delta-manifest-and-change-accounting.md`](version-delta-manifest-and-change-accounting.md),
[`recovery-drills-for-false-closure-and-leakage.md`](recovery-drills-for-false-closure-and-leakage.md),
[`ft0181-closure-evidence-checklist.md`](ft0181-closure-evidence-checklist.md),
and `AS-0247`, `AS-0248`, `AS-0249`, `AS-0250`, and `AS-0251`.
