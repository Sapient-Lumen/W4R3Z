# Unpreventable damage receipt — rev0174

## Why this cut exists

The prevention/replacement seam is one of the riskiest places for a proof-carrying MTG kernel because it sits between an intended damage event and the final state mutation. The current scaffold already had finite prevention shields and typed shield-consumption records, but unpreventable damage was still missing as an executable/auditable edge. That matters because an auditor should be able to tell the difference between “no shield applied” and “a shield was applicable, was observed, but did not prevent or decrement because the damage was unpreventable.”

Online grounding for this turn used Wizards' current rules page and the current TXT rules artifact observed effective 2026-06-19. The local official-rules manifest remains metadata-only and still avoids bundling official rules text. This revision changes local behavior and evidence around CR 615.12-style unpreventable damage; it is not a full rules-source refresh/diff revision.

## What changed

rev0174 adds a narrow unpreventable-damage path:

- `DamageRecord::unpreventable` records that the damage cannot be prevented.
- `DamageRecord::protection_prevention_ignored` records that protection would have prevented the damage, but was ignored because the damage was unpreventable.
- `DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage` records applicable finite prevention shields as no-effect rows.
- `deal_unpreventable_damage_to_target(...)` exposes the path without changing the ordinary `deal_damage_to_target(...)` contract.
- `apply_unpreventable_damage_prevention(...)` records applicable shields without reducing or expiring them.

The receipt range is still linked from `DamageRecord::first_damage_prevention_record_index` plus `damage_prevention_record_count`, but the no-effect row contributes zero to `DamageRecord::prevented`. The durable distinction is now explicit: shield-consumption rows prove prevention; unpreventable rows prove prevention was considered and left intact.

## Audit/refactor work

The damage implementation now funnels ordinary and unpreventable damage through a shared internal helper so protection, source snapshots, target snapshots, lifelink/deathtouch metadata, and final damage application stay structurally aligned. Validation now rejects the important corruptions:

- unpreventable damage that records a prevented amount;
- unpreventable damage that says protection prevented it;
- protection-ignored flags on preventable damage;
- shield-consumption rows linked to unpreventable damage;
- no-effect unpreventable rows linked to preventable damage;
- no-effect rows that reduce shield remaining or link to zone-change expiry.

`tools/audit_datacube.py` also gained probes for the new prevention seam so future archive audits check for the no-effect receipt kind, unpreventable API, engine hook, validator diagnostic, and regression test.

## Remaining risk

This is deliberately not the full rule-616 replacement/prevention choice kernel. Missing pieces include affected-player choice among multiple replacement/prevention effects, source-filtered shields, redirection, self-replacement ordering, card-text parsing, prevention duration templates, and simultaneous damage batches. The gain is narrower but substantial: unpreventable damage no longer disappears into ordinary damage records, and applicable shields are no longer invisible to replay/audit consumers.
