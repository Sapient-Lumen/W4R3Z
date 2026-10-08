# Mission kernel rev0267

Date: 2026-06-16
Revision: rev0267
Status: active first-read kernel, field-execution bias, and no-new-doctrine posture while `FT-0181` remains owner-evidence blocked.

## Mission sentence

Use AI in education only where it preserves human agency, protects the learning construct, keeps consequential authority contestable, and can support public claims with evidence that is no stronger than the source truth actually received.

For this archive, the mission now has one practical test: can `AIEDU-SR-003` move through one bounded owner-reviewed packet without asking for raw learner records, protected facts, small cells, hidden authority, vendor-only claims, or learning-effectiveness language?

## Current live risk

The riskiest failure is not a missing registry. It is an execution gap: the archive can route, lint, and explain the `FT-0181` field path, but a real `SRC2+` owner-reviewed packet is still absent.

The second risk is attention waste. A maintainer can burn the session proving the same no-real-data state across many surfaces instead of preparing, sending, clocking, triaging, or closing a bounded owner-contact attempt.

The third risk is claim creep after a small packet arrives. Even a viable eight-row reply would initially support only a bounded process/readiness claim, not learning, safety, access, workload, compliance, scale, or effectiveness.

## First-read kernel

Read these surfaces before expanding into the wider cube. The point is to move from mission to field action without reopening the branch tail.

| Order | Surface | Use |
|---:|---|---|
| 1 | [`START_HERE.md`](../../START_HERE.md) | Single current command path and hard prohibitions. |
| 2 | [`AGENTS.md`](../../AGENTS.md) | Maintainer rules for this session and the live gate. |
| 3 | [`docs/00-meta/mission-kernel-rev0267.md`](mission-kernel-rev0267.md) | This compact mission/action kernel. |
| 4 | [`docs/00-meta/cube-deep-audit-rev0267.md`](cube-deep-audit-rev0267.md) | Deep audit and anti-waste diagnosis for the revision. |
| 5 | [`docs/30-operations/ft0181-owner-request-packet-prep.md`](../30-operations/ft0181-owner-request-packet-prep.md) | Prepare the local outbound packet and field-texture memo. |
| 6 | `tools/decide_ft0181_field_next_action.py` | Ask for the single next bounded command. |
| 7 | `tools/prepare_ft0181_owner_request_packet.py` | Generate the email, blank CSV, checklist, no-packet note, field-texture memo, and manifest. |
| 8 | `tools/record_ft0181_owner_contact_status.py` | Record sent, one re-ask, or no-owner-packet clocks locally. |
| 9 | [`docs/30-operations/ft0181-eight-row-owner-reply-sheet.md`](../30-operations/ft0181-eight-row-owner-reply-sheet.md) | The exact minimized owner ask. |
| 10 | [`docs/30-operations/ft0181-owner-reply-intake-bundle.md`](../30-operations/ft0181-owner-reply-intake-bundle.md) | Route returned CSVs without copying raw answers into the archive. |
| 11 | [`docs/30-operations/ft0181-owner-reply-workbench-seed.md`](../30-operations/ft0181-owner-reply-workbench-seed.md) | Seed only a local, not-accepted workbench after `PROCEED-STAGED`. |
| 12 | [`docs/30-operations/ft0181-public-outcome-kernel.md`](../30-operations/ft0181-public-outcome-kernel.md) | Bound first public/process outcomes before any evidence arrives. |
| 13 | [`docs/20-governance/education-ai-deployment-risk-crosswalk.md`](../20-governance/education-ai-deployment-risk-crosswalk.md) | Keep education-specific risk classes in view. |
| 14 | [`docs/20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md) | Match claims to source truth. |
| 15 | [`docs/20-governance/ai-action-authority-register-and-delegation-ceilings.md`](../20-governance/ai-action-authority-register-and-delegation-ceilings.md) | Stop hidden send/write/penalty/protected-route authority. |
| 16 | [`docs/00-meta/branch-tail-freeze-and-pruning-audit-rev0267.md`](branch-tail-freeze-and-pruning-audit-rev0267.md) | Keep historical branches in retrieval mode rather than doctrine growth. |

Everything else remains reachable through `SURFACES.json`, `BRANCH_FAMILY_INDEX.json`, `ARCHIVE_INDEX.md`, and `context-pack.json` after the field path is understood.

## One-session action bias

A maintainer should spend most of the session on one of these concrete moves:

1. run `make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003`;
2. run the emitted packet-prep command in `scratch/`;
3. adapt and send the generated owner email outside the archive;
4. rerun the router and record the dated sent clock outside the release archive;
5. triage a real returned CSV through the router; or
6. record a bounded `NO_OWNER_PACKET` when the clocks and one clarification are exhausted.

If none of those can be done in the current environment, the useful substitute is to reduce friction for exactly one of those moves, not to add a new control family.

## Change budget while `FT-0181` is blocked

Allowed changes:

- improve the generated first-contact packet;
- improve local field-texture capture without making it evidence;
- compress first-read navigation;
- prune or freeze branch-history routes;
- clarify allowed and forbidden public language;
- repair a validator or route that would block a real packet incorrectly.

Disallowed changes unless a real packet exposes a gap:

- new schemas, registries, or validators;
- new branch sibling documents;
- broader owner data requests;
- direct intake commands that bypass the router;
- public claims about learning, safety, access, workload, compliance, scale, or effectiveness.

## Closure boundary

This kernel does not close `FT-0181`, does not contact an owner, does not import evidence, and does not prove that an AI service works. It exists to stop the archive from mistaking navigation or governance growth for field progress.
