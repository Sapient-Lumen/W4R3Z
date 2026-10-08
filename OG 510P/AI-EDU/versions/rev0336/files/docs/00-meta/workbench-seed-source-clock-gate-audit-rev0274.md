# Workbench seed source-clock gate audit rev0274

## Problem found

Rev0273 correctly required returned CSV intake to name an active bounded contact-status clock. The next false-progress seam sat one step later: a local intake bundle manifest could be hand-edited, copied, or downgraded before `make owner-reply-workbench-seed` ran. The seed tool verified receipt, triage, and staging hashes, but it trusted the bundle's source-clock summary rather than revalidating the referenced scratch `contact-status.json`.

That meant an older or forged `PROCEED-STAGED` bundle could still route a maintainer into manual workbench review. The seed would remain non-evidence, but it would make the path look more complete than it was.

## Rev0274 correction

Rev0274 adds a source-clock gate to the workbench seed step:

- `tools/seed_owner_packet_workbench.py` now revalidates the `source_contact_status.reference` preserved by the intake bundle.
- The reference must resolve under archive `scratch/`, point to an existing `contact-status.json`, and pass the shared active contact-status integrity check.
- The bundle summary must match the referenced contact-status fields for status, sent date, due date, status date, attempt count, and evidence state.
- The generated `workbench-seed.json` now preserves a `source_contact_status` block with `revalidated_for_seed: true`.
- `tools/decide_ft0181_field_next_action.py` now blocks old or edited workbench seeds before routing to manual workbench review.
- `tools/ft0181_field_guards.py` centralizes the seed integrity check so the router and future validators do not diverge.

## Why this is substantive

This does not add another approval meeting or registry. It hardens the exact place where a plausible local bundle turns into the human workbench handoff. The question is narrow: did this seed come from a `PROCEED-STAGED` intake bundle that still traces back to the bounded contact clock that made a returned owner CSV plausible?

A valid answer still does not prove the CSV is truthful. It only prevents a stale, copied, or hand-edited local bundle from skipping the field-state machine.

## Refactor result

The `FT-0181` local path now has a continuous non-evidence chain:

1. prepared packet;
2. send log;
3. sent or re-ask contact status;
4. returned CSV routed through the active contact clock;
5. intake bundle preserving the source contact status;
6. workbench seed that revalidates that source status and stays `NOT_ACCEPTED`;
7. manual owner-packet workbench review before any custody, acceptance, public-summary, readout, signoff, or closure step.

## Remaining risk

This still cannot prove delivery, owner identity, owner truthfulness, or source custody. Those are field and downstream custody problems. Rev0274 only prevents the local workbench handoff from outrunning the contact-clock provenance gate.
