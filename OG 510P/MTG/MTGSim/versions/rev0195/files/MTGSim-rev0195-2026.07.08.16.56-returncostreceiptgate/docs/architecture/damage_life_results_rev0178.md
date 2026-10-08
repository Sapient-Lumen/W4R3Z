# rev0178 — damage life-result links

## Why this cut exists

rev0177 closed the damage/counter drift seam for planeswalkers and battles. The next risky positive-result seam was player damage and lifelink: `DamageRecord::dealt` said damage happened, while the resulting `LifeChangeRecord` rows for player life loss and lifelink life gain were only adjacent in the event stream. Replay, audit, and later replacement/prevention work had to infer that those life rows belonged to the damage event.

The online grounding is narrow and deliberately not bundled: the current public rules surface identifies damage to a player as life loss when infect is not involved, and lifelink as a simultaneous additional life-gain result. The official rules page remains a consulted reference, not executable source text inside the datacube.

## What changed

`DamageRecord` now owns the life-result evidence it summarizes:

- `first_damage_life_change_record_index`
- `damage_life_change_record_count`

`LifeChangeRecord` rows that are damage results now also carry:

- `damage_record_index`
- `damage_source`
- `damage_source_zone_change_index`
- `damage_target`
- `damage_result`
- `lifelink_result`

During `deal_damage_to_target(...)`, the engine snapshots the life-change stream before applying damage results. Player damage links the damaged player's loss row; lifelink links the source controller's gain row for both player and object damage. The linked rows record the same source identity, source zone-change incarnation, and target snapshot as the owning `DamageRecord`.

Validation now rejects drift instead of leaving it to event ordering:

- player damage with nonzero dealt damage must own a life-loss range;
- lifelink damage with nonzero dealt damage must own a life-gain range;
- impossible/not-dealt target-type damage may not carry life-result metadata;
- linked life rows must backlink to the owning damage record;
- linked rows must match source, source zone-change identity, target snapshot, amount, row kind, and sequence ordering;
- player damage must have exactly one loss row, and lifelink damage exactly one gain row.

The focused regression covers both player and object lifelink damage. It corrupts the `DamageRecord` life range and a linked `LifeChangeRecord` backlink to prove validation catches the seam locally.

## What did not change

This is still not the full damage-result replacement lattice. Infect poison counters, wither/infect -1/-1 counters, toxic, source-owner fallback for controllerless lifelink, damage redirection, life-gain/life-loss replacement effects, and simultaneous batch semantics remain future work. The useful movement is narrower: the current damage-to-life results are now first-class, typed, and challengeable.

## Audit/refactor note

This cut deliberately reuses the existing typed streams instead of inventing another registry. `DamageRecord` becomes the owner of its life-result rows, and `LifeChangeRecord` gains a backlink only when it is truly caused by damage. That turns an order-based inference into a local contract.
