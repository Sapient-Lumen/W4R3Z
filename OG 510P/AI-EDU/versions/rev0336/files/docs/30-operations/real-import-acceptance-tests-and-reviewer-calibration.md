# Real-import acceptance tests and reviewer calibration

`FT-0181` should close only when a real pilot import changes or confirms decisions under a reviewed
acceptance protocol. This surface adds a small acceptance harness so the archive can distinguish
four things that otherwise blur together: import lane readiness, source owner review, normalized
candidate records, and closure-quality evidence.

The rule is: **a real import is accepted only when reviewers agree on the decision effects, not
merely when JSON validates**.

## Acceptance states

| Code | Meaning | Closure posture |
|---|---|---|
| `AC0` | No acceptance packet | `FT-0181` cannot close. |
| `AC1` | Synthetic or realistic examples only | Keep queued; examples can test tooling only. |
| `AC2` | Source dictionary, import map, owner workbench, and decision-board path reviewed | Keep queued unless an `SRC2+` record is staged. |
| `AC3` | Candidate `SRC2+` service record normalized | Review; do not close until decisions are compared. |
| `AC4` | Reviewer calibration complete | May move to closure review if required tests pass. |
| `AC5` | Decision-delta and redaction effects accepted | May close if manifest, record, and public-summary checks pass. |
| `AC6` | Post-import schema pruning or revision completed | Close and cite imported record set. |
| `ACX` | Protected, conflicting, unsafe, or legally constrained source | Quarantine; do not normalize into examples. |

`AC3-AC6` require source truth class `SRC2`, `SRC3`, or `SRC4`. `AC0-AC2` can improve the lane, but
they do not close `FT-0181`.

## Required acceptance tests

| Test | What must be true |
|---|---|
| Source class | Source truth class is `SRC2+` and record owner can name the source system. |
| Dictionary | Local source fields have meanings, sensitivity classes, and import actions. |
| Minimization | Protected facts, raw learner traces, and security exploit details are excluded before commit. |
| Schema | Candidate service record validates and names source status/confidence honestly. |
| Decision delta | Reviewers can say which fields changed authority, memory, evidence, proof, redaction, lifecycle, stop, or continuity decisions. |
| Public rendering | Audience summaries pass profile and sector-adapter smoke tests without overclaiming. |
| Decision board | Authority, evidence, construct, public-summary, and lifecycle slices are filled before claim or lifecycle changes. |
| Calibration | At least two reviewers agree on closure-critical decisions, or disagreements are recorded as blocks. |
| Pruning | Fields that did not change decisions are trimmed, kept local, or explicitly left optional. |

## Reviewer calibration

Use at least two reviewers for the first real import whenever possible:

1. a record or service owner who understands local source fields;
2. a governance reviewer who understands authority, evidence, proof, and public-claim limits;
3. a support or security reviewer when protected routes or agentic tools are involved.

The reviewers do not need to agree on broad philosophy. They must agree on closure-critical facts:
source class, protected exclusions, action authority, evidence grade, public claim limits, stop
triggers, and whether schema changes are justified.

## Disagreement handling

| Disagreement type | Default disposition |
|---|---|
| Source meaning unclear | Block import and return to dictionary. |
| Protected/support status unclear | Keep local or quarantine; do not publish. |
| Authority ceiling disputed | Use the lower authority ceiling until reviewed. |
| Evidence grade disputed | Use the weaker public claim until renewed. |
| Public summary disputed | Suppress claim or route to narrower audience profile. |
| Schema field disputed | Leave optional or local until a second real record confirms need. |

## Acceptance packet contract

Acceptance packets live in `examples/real-import-acceptance/` and declare:

- the related followthrough item;
- acceptance state and source truth class;
- whether closure is permitted;
- referenced readiness manifests, source dictionaries, import maps, and candidate records;
- required test results;
- reviewer calibration and unresolved blocks;
- last reviewed date.

`tools/check_real_import_acceptance.py` fails if a packet permits closure without `SRC2+`, `AC5+`,
passing required tests, no unresolved closure blocks, and at least one referenced readiness
manifest, dictionary, import map, and candidate record. rev0219 adds separate request, failure-fixture,
and release-candidate validators so acceptance cannot substitute for the minimum packet, rejection
coverage, or queue/receipt agreement.

## No-real-data posture

The shipped packet `ACCEPT-FT0181-NO-REAL-DATA` intentionally has `closure_permitted: false`.
Rev0233 keeps it at `AC2`: the source dictionary, import map, owner packet workbench, and first-packet decision board are ready for review, while the archive still has no real pilot record to accept.

## Current archive bet

The first real pilot import should be treated like a calibration event, not a data migration. Its
main value is to reveal which fields change decisions, which fields should be pruned, and which
public claims must become narrower.

See [`pilot-source-data-dictionary-template.md`](pilot-source-data-dictionary-template.md),
[`import-readiness-manifest-and-no-real-data-gate.md`](import-readiness-manifest-and-no-real-data-gate.md),
[`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md),
[`ft0181-owner-packet-workbench.md`](ft0181-owner-packet-workbench.md),
[`ft0181-first-packet-decision-board.md`](ft0181-first-packet-decision-board.md),
[`import-negative-fixtures-and-failure-mode-catalog.md`](import-negative-fixtures-and-failure-mode-catalog.md),
[`decision-delta-log-template-and-field-pruning-rules.md`](decision-delta-log-template-and-field-pruning-rules.md),
[`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md),
and `AS-0230`, `AS-0233`, `AS-0234`, and `AS-0235`.


## Post-decision ticket acceptance check

After the first-packet decision board, acceptance must verify a compact change ticket. The ticket names allowed changes, prohibited changes, public claim ceiling, rollback owner, rollback triggers, and closure boundary. Without it, a packet may remain reviewable, but it cannot authorize public-summary, lifecycle, schema, validator, or closeout changes.

A no-real-data rehearsal must keep this test blocked, because a blank ticket would make the archive look ready to change service state without the owner packet that justifies the change.


## Rev0236 end-window acceptance addendum

A real acceptance packet must now confirm that any paused, rolled-back, or completed live window has an end-of-window readout. The readout must name claim-family effects, public language after the readout, rollback/stop outcome, fields to trim, reviewer disagreements, and why the readout does not close `FT-0181` by itself.


## Post-readout action acceptance

Rev0237 requires the acceptance harness to block closure when a readout disposition has no owned
post-readout action dispatch and due-date recheck. The dispatch must name the owner action, next evidence ask, fields to
re-ask, fields to drop, public-language action, and recheck date before a stopped, rolled-back,
rerun, continued, quarantined, or no-change window alters lifecycle, public language, schema,
validator, closeout, or closure posture.
