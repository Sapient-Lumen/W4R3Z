# Operator handoff and maintainer runbook

Late-stage AI-EDU work is now less about adding theory and more about preserving release discipline.
This surface tells a future maintainer what to read, what to run, what not to claim, and how to
unblock the remaining real-import gate without turning examples into evidence.

The rule is: **a handoff is valid only when it preserves the archive's evidence status**. A clean
release can still have a live item; it cannot hide that item, soften it into a done claim, or publish
synthetic examples as pilot proof.

## Operator handoff states

| Code | Meaning | Maintainer action |
|---|---|---|
| `OH0` | local draft | Run lint before sharing. |
| `OH1` | lint-clean internal handoff | Read re-entry, queue, receipt, and release candidate together. |
| `OH2` | ready-but-not-closed release handoff | Ship only with the external-data gate visible. |
| `OH3` | real data requested | Track owner, source class, prohibited fields, and decision questions. |
| `OH4` | real import staged | Require dictionary, acceptance, render, delta, and closeout review. |
| `OH5` | closure-ready import | Close `FT-0181` only after the queue, receipt, closeout, and release candidate agree. |
| `OHX` | evidence confusion, protected leakage, or fake closure | Stop packaging and quarantine the affected records. |

`OH2` is the current intended posture: the archive can be used, inspected, and extended, but the
first real pilot import has not happened.

## First read order for a maintainer

1. `START_HERE.md` for the current posture.
2. `AGENTS.md` for operating constraints.
3. `FOLLOWTHROUGH_QUEUE.json` and `REVISION_RECEIPT.json` together.
4. [`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md).
5. [`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md).
6. [`real-pilot-record-import-and-normalization-workflow.md`](real-pilot-record-import-and-normalization-workflow.md).
7. [`real-import-acceptance-tests-and-reviewer-calibration.md`](real-import-acceptance-tests-and-reviewer-calibration.md).
8. [`real-import-closeout-board-and-decision-minutes.md`](real-import-closeout-board-and-decision-minutes.md).

Then run `python3 tools/run_lint_suite.py`. Do not edit from memory if lint says the queue, receipt,
release candidate, or surface map disagree.

## Claims a maintainer must not make

- Do not claim all followthrough is closed while `FT-0181` is queued.
- Do not claim a real pilot record has been imported unless an `SRC2+` source passes readiness,
  acceptance, closeout, render, and decision-delta review.
- Do not cite realistic service records as evidence of effectiveness, safety, workload savings, or
  durable learning.
- Do not publish protected support facts, raw learner traces, security payloads, or small-cell
  subgroup facts to make the service look more evidenced.
- Do not promote a service whose evidence clock is expired merely because the schema record still
  validates.

## Handoff JSON contract

Machine-readable handoff records live in `examples/operator-handoffs/`. They name the current
revision, remaining followthrough items, startup surfaces, required commands, allowed next actions,
forbidden claims, stop conditions, and first real-import unblocker.

`tools/check_operator_handoffs.py` verifies that the handoff record matches the current receipt and
queue, that referenced startup surfaces exist, and that the no-fake-import assertion remains true
when `FT-0181` is live.

## Maintainer stop conditions

Stop the release and open a local incident note if any of these occur:

- a service record changes from `realistic_example` to real-import status without closure-ready
  readiness and acceptance packets;
- a public summary includes stronger claims than the evidence grade supports;
- protected support, disability, counselling, discipline, immigration, hardship, or language-access
  facts appear in a public artifact;
- raw prompt strings, security exploit strings, credentials, or tool payloads appear in examples;
- the queue says `FT-0181` is done but no closeout board permits closure;
- a new branch repeats an existing pattern without a new actor, stakes, authority, memory, proof,
  owner, or evidence shift.

## Current archive bet

A maintainer should be able to resume the archive without reconstructing the whole session. The
handoff layer exists because late-stage governance failures are often boring: a status field drifts,
a public summary overclaims, a schema example becomes evidence by implication, or a live external
block disappears from the release story.

See [`service-lifecycle-deprecation-and-archive-exit-rules.md`](service-lifecycle-deprecation-and-archive-exit-rules.md),
[`real-import-closeout-board-and-decision-minutes.md`](real-import-closeout-board-and-decision-minutes.md),
[`../20-governance/evaluator-independence-and-evidence-contamination-controls.md`](../20-governance/evaluator-independence-and-evidence-contamination-controls.md),
and `AS-0236`.
