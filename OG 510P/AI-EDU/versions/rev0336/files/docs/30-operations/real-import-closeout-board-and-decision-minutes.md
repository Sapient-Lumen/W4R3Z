# Real-import closeout board and decision minutes

Readiness, source dictionaries, acceptance packets, render checks, and negative fixtures prepare the
first real import. They still need a final closeout moment that says what changed, what did not
change, what was removed, what rollback route exists, and whether `FT-0181` can honestly close.

The rule is: **a real import closes only by decision minutes, not by a passing JSON file alone**.

## Closeout states

| Code | Meaning | Queue posture |
|---|---|---|
| `CB0` | no real data | Keep `FT-0181` live. |
| `CB1` | request sent or blocked | Keep live; track owner and source class. |
| `CB2` | source packet received | Keep live until dictionary and minimization pass. |
| `CB3` | candidate record normalized | Keep live until acceptance and public render pass. |
| `CB4` | acceptance mostly complete but unresolved block remains | Keep live and name the block. |
| `CB5` | closure-ready with `SRC2+` evidence and decision delta | May close if receipt, queue, and release candidate agree. |
| `CB6` | closed and public summaries updated | `FT-0181` may be done. |
| `CBX` | protected leakage, fake source, unsafe payload, or evidence laundering | Quarantine and do not close. |

## Closeout questions

A closeout board answers seven questions:

1. What source truth class is being accepted, and who owns the source meaning?
2. Which candidate service record changed a decision?
3. Which fields were pruned because they were decision-neutral, protected, or unsafe?
4. Which claim-family evidence grades, expiry dates, or public claims changed?
5. Which action-authority, memory, construct, proof, security, or fallback fields changed?
6. Which public summaries were rendered, suppressed, or rewritten?
7. Which lifecycle state now applies: sandbox, pilot, recurring, watch, deprecate, archive-only, or quarantine?
8. Which post-decision change ticket authorizes, blocks, trims, stages, or rolls back the concrete change?

If the board cannot answer these without raw learner traces, protected facts, or exploit payloads,
the import is not ready for public archive normalization.

## Decision minutes contract

Closeout records live in `examples/real-import-closeouts/`. They reference the readiness manifest,
acceptance packet, release-candidate state, lifecycle decision, candidate service records, and
unresolved blocks.

`tools/check_real_import_closeouts.py` verifies that a closeout record references known artifacts,
uses a valid closeout state, and does not permit `FT-0181` closure without `SRC2+` source class,
closure-ready state, no unresolved blocks, and an evaluator-independence attestation.

## Non-closure is useful

A closeout board may produce a valuable non-closure decision. It can say:

- the import request is well formed but no real packet exists;
- a source packet exists but carries protected fields that must stay local;
- the candidate record validates but does not change decisions;
- public summaries overclaim and must be rewritten;
- lifecycle decision is watch or deprecate rather than promote;
- a decision board is complete but the post-decision change ticket blocks overreach;
- reviewer disagreement is unresolved and closure remains blocked.

That is still progress because it prevents fake completion.

## Current archive bet

The closeout board prevents the last live item from disappearing through tool success alone. A real
pilot import should leave decision minutes that explain the schema, evidence, public claim, lifecycle, and rollback consequences in ordinary language.

See [`operator-handoff-and-maintainer-runbook.md`](operator-handoff-and-maintainer-runbook.md),
[`service-lifecycle-deprecation-and-archive-exit-rules.md`](service-lifecycle-deprecation-and-archive-exit-rules.md),
[`../20-governance/evaluator-independence-and-evidence-contamination-controls.md`](../20-governance/evaluator-independence-and-evidence-contamination-controls.md),
and `AS-0239`.


## Rev0236 closeout addendum

Closeout minutes must not treat a completed first live window as closure. They must cite the end-of-window readout and the post-readout action dispatch and due-date recheck, then show which claim families remain unmade, narrowed, removed, or merely eligible for bounded continuation.


## Post-readout action boundary

A closeout board must not act on a readout disposition until the post-readout dispatch names owner
action, allowed and prohibited next actions, fields to re-ask, fields to drop, public-language action,
and recheck date. A dispatch can return the packet to the owner, stop, roll back, rerun narrower,
continue under the same ceiling, quarantine, or trim a no-change ask. It cannot prove outcomes or
close `FT-0181` by itself.
