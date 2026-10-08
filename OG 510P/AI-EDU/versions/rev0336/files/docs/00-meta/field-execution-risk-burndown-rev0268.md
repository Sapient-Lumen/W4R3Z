# Field execution risk burndown rev0268

Date: 2026-06-16
Revision: rev0268
Status: priority risk burn-down and small refactor record; not evidence, not owner contact, and not closure.

## Why this pass exists

The cube's highest risk is no longer conceptual coverage. The live risk is that `FT-0181` remains perfectly governed and never fielded. Rev0268 therefore changes the parts of the archive that most directly affect whether a maintainer can complete the first owner-contact cycle.

## Priority risk table

| Risk | Why it matters | Rev0268 change | Remaining external action |
|---|---|---|---|
| Prepared packet never sent | A prepared packet is not evidence and does not change the source-truth state. | Packet prep now emits `SEND-NOW-BRIEF.md`, a one-page operator aid that names the exact attachment, what not to attach, and the after-send router command. | A human must still send or adapt the email outside the archive. |
| Stale scratch output causes hand edits | Re-running a command against an existing output directory can push maintainers toward manual date edits or duplicate notes. | `make owner-request-packet` and `make owner-contact-status` now expose `OVERWRITE=1`; packet overwrite removes stale files before rebuilding. | Use overwrite only for local scratch regeneration, not for evidence acceptance. |
| Local implementation texture gets confused with evidence | Owner-route friction is useful, but it can become accidental evidence if copied into release surfaces. | `FIELD-TEXTURE-MEMO.md` remains local-only; `SEND-NOW-BRIEF.md` repeats that it is not evidence and cannot support claims. | Keep recipient names, owner answers, learner facts, protected facts, and public claim language out of both files. |
| Oversized historical surfaces steal attention | The 26k-word continuity-cost surface is useful but not relevant to the current AIEDU-SR-003 field gate. | The surface now has a rev0268 compression/refactor note: read the kernel only unless continuity-cost work is active. | Do not reopen continuity-cost doctrine while `FT-0181` lacks owner context. |
| Public language outruns source truth | A small owner reply can tempt generalized claims. | The public-outcome kernel remains the first claim boundary and is linked from the mission kernel and start path. | Do not claim learning, safety, access, workload, compliance, scale, or effectiveness without later accepted evidence. |

## Refactor performed

This was a small, execution-biased refactor rather than a new doctrine layer:

- made the existing overwrite capability reachable through `make` for packet and contact-status generation;
- changed packet overwrite semantics so stale local files are removed instead of silently persisting;
- added `SEND-NOW-BRIEF.md` to the generated owner packet;
- updated packet validation so the brief, packet version, and overwrite behavior are lint-covered;
- added a compression note to the largest operational surface, `docs/30-operations/no-fault-transition-cost-absorption-and-fee-waiver-rules.md`;
- updated first-read navigation so a maintainer sees the field action path before large historical stacks.

## What did not change

No owner was contacted. No returned CSV exists. No `SRC2+` evidence was imported. No intake bundle was accepted. No workbench seed became acceptance evidence. No live-window readout exists. No closure minutes or public claim upgrade are supported.

## Next irreversible move

The next meaningful move cannot be another archive surface unless a real packet exposes a missing representation. The next move is:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003
make owner-request-packet OUT=scratch/owner-request-packets/aiedu-sr-003-first-contact
```

Then open `scratch/owner-request-packets/aiedu-sr-003-first-contact/SEND-NOW-BRIEF.md`, send or adapt the generated email outside the archive, and rerun the router to record the dated contact clock.

## Boundary

This burn-down record is not evidence, does not close `FT-0181`, and does not prove service effectiveness. It is an anti-waste record of the riskiest completion failures and the small code/docs changes made to reduce them.
