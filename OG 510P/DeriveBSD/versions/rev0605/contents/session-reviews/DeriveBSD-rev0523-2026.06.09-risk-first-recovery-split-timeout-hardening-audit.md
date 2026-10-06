# DeriveBSD rev0523 risk-first recovery split and timeout-hardening audit

Date: 2026-06-09
Project version: 2026-06-09r555
Archive lineage: rev0522 -> rev0523

## Executive summary

This revision intentionally avoided another broad registry/doctrine pass. It
spent the session budget on two completion-risk surfaces that directly affect
whether future cloudtainer work can finish and whether the post-detach cube can
keep moving without smuggling exact fixture literals into runtime contracts.

The first change hardens `tools/hygiene.py` ledger execution. A timed-out check
is now launched in its own process group and terminated as a process group, with
a short grace period and SIGKILL escalation. The ledger schema and checker now
require explicit timeout-cleanup evidence fields, so future ledgers say whether
they isolated the child process group and what kill scope was used. This fixes a
real cloudtainer risk: killing only the direct Python child can leave nested
build/smoke children alive, wasting the interactive window and making a timeout
look cleaner than it really was.

The second change completes one p0 schema-cube refactor: post-detach recovery
evidence is now split into a generic runtime schema and an exact fixture schema.
The runtime schema no longer carries the canonical example's exact digest
literals as runtime law; exact digest assertions moved to
`spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json`.
The recovery checker validates the canonical example against both schemas and
validates negative fixtures against both. Downstream post-detach checkers were
then corrected so they require digest shape from the runtime schema and exact
canonical digest tokens only from the fixture schema.

## Concrete implementation changes

- Added process-group timeout cleanup to `tools/hygiene.py`.
- Added ledger fields: `process_group_isolated`, `timeout_kill_scope`,
  `timeout_termination_signal`, and `timeout_grace_seconds`.
- Extended `spec/cube.hygiene.run.ledger.schema.json` and
  `tools/check_cube_hygiene_run_ledger.py` so the new timeout semantics are not
  just implementation folklore.
- Split `spec/removable.media.local.post_detach.recovery.evidence.schema.json`
  into a runtime schema plus
  `spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json`.
- Updated `tools/check_removable_media_local_post_detach_recovery_evidence.py`
  to validate both runtime and fixture schemas.
- Updated downstream post-detach checkers whose schema-field audits still
  expected exact recovery-chain digests in the runtime schema:
  - revocation tombstone
  - fresh authority receipt
  - fresh authority consumption receipt
  - successor-index cutover receipt
  - successor-index checkpoint receipt
  - reader admission receipt
  - reader use receipt
  - query projection
  - export bundle
- Regenerated the schema audit report, refactor backlog, hygiene checkset
  manifest, hygiene run ledger, context pack, artifact index, and doc catalog.
- Refreshed README, CHANGELOG, docs/current, and the recovery-evidence/ADR
  surfaces for 2026-06-09r555.

## Cube audit result after the split

The schema cube now reports:

- 449 schemas
- 467 canonical examples
- 25 const-heavy schemas
- 34 runtime-contract-shaped schemas
- 11 exact fixture schemas
- 0 dotted-kind filename mismatches
- 434 schemas with canonical examples
- 15 schemas without canonical examples

The refactor backlog now reports:

- 25 total backlog items
- 11 completed items
- 14 open items
- 17 post-detach items
- 6 audit-next targets
- highest remaining const count: 201

The next p0 targets remain the post-detach reader-use ledger family, fresh
authority consumption receipt, successor-index checkpoint receipt, and launch
evidence. Those are now clearer targets because recovery evidence no longer
mixes runtime contract shape with exact fixture literals.

## What was risky or wasteful

The most severe completion risk was the hygiene runner timeout behavior. In a
cloudtainer, a single expensive checker can consume the remaining session if its
children outlive the wrapper. The new process-group cleanup does not make slow
checks fast, but it makes bounded runs actually bounded and makes timeout
receipts more truthful.

The most important cube-design risk was fixture literal bleed. Recovery evidence
is a join point for many post-detach receipts, so keeping exact downstream
digests in the runtime schema would have made every future receipt split harder.
The fact that several downstream checkers failed after the split was useful:
those failures showed real coupling rather than abstract technical debt.

The biggest remaining waste is still front-door size and generated-doc churn.
This revision did not try to solve that. It only kept generated surfaces in sync
after the substantive changes. The next non-schema infrastructure win should be
a bounded/generated front door that stops README and the numbered index from
becoming hand-maintained release ledgers.

## Validation evidence

Fresh ledgers were written for this revision:

- `session-reviews/DeriveBSD-rev0523-2026.06.09-release-critical-hygiene-ledger.json`
  — release-critical, 35/35 passed.
- `session-reviews/DeriveBSD-rev0523-2026.06.09-post-detach-hygiene-ledger.json`
  — post-detach, 39/39 passed.

Additional targeted profiles passed:

- `tools/hygiene.py --profile schema-cube-audit`
- `tools/hygiene.py --profile generated-surface`

The linked archive was also zip-tested and checked for accidental Python
bytecode artifacts before handoff.

## Next recommendation

Continue the schema-cube refactor with the highest-risk remaining p0 target:
`spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json`.
That family is close to the actual post-detach observation boundary, so splitting
it early should reduce future coupling before retention, expiry, and rate-limit
receipts accumulate more exact fixture law in runtime schemas.
