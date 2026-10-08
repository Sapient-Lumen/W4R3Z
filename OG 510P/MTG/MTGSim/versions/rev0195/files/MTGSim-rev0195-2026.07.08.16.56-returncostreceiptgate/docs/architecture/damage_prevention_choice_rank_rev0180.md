# rev0180 — Prevention Choice Audit

## Mission pressure

The heart of MTGSim remains trusted transitions: one authoritative state plus one explicit legal choice should produce one deterministic next state and enough typed evidence to validate, replay, branch, fuzz, search, and explain it. The riskiest missing mission surface is not another registry entry; it is the event-replacement/prevention seam where multiple applicable effects may be available and the cube must prove why a particular effect was consumed first.

## Online research used

This pass rechecked the official Wizards rules page and current Comprehensive Rules TXT metadata online. The live rules surface observed for this session lists an effective date of 2026-06-19 and exposes the replacement/prevention interaction cluster around rules 614, 615, and 616. The revision records URLs and observations only; official rules documents remain excluded from the datacube.

Key external anchors recorded for future private refresh/diff work:

- Official rules page: https://magic.wizards.com/en/rules
- Current observed TXT: https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.txt
- Current observed PDF: https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.pdf

## Code-bearing change

rev0180 turns a risky implicit behavior into a typed, auditable seam:

- `DamagePreventionShield` now carries `choice_rank`, a deterministic stand-in for an affected-player/object choice until the full interactive rule-616 choice pipeline exists.
- `add_damage_prevention_shield` accepts the rank and persists it in shield creation evidence and snapshots.
- Damage prevention application now collects applicable shield candidates, orders them deterministically by choice rank, and emits pass-by-pass application rows.
- `DamagePreventionRecord` now carries `affected_player`, `choice_rank`, `candidate_count`, `pass_index`, and `chosen_among_multiple` for consumed shields and no-effect unpreventable-damage applications.
- Validation rejects missing or contradictory application metadata and verifies affected-player consistency against the damaged player or object controller/owner.
- Snapshot hashing includes the new shield and record fields, so replay/state identity sees this semantic choice evidence.

## Refactor/audit substance

The refactor removed an insertion-order dependency from prevention shield application. Prior revisions could be deterministic but semantically under-explained: two prevention shields on the same recipient were consumed according to storage order, and replay evidence did not say how many candidates existed or whether a real choice seam had been crossed. This is precisely the kind of quiet engine debt that can make later card support misleading.

rev0180 makes the seam explicit without claiming the full rules problem is solved. The engine now has a narrow, testable bridge: deterministic choice-rank ordering today, interactive affected-player/APNAP choice integration later.

## Remaining risk

This is still a scaffold. It does not yet implement the complete replacement/prevention event system with interactive affected-player ordering, self-replacement precedence, APNAP tie handling for every simultaneous choice class, or source/card-specific replacement filters. The next high-value work should connect this evidence format to the broader replacement event chain rather than expanding prose registries.

## Validation evidence

- C++ release tests: 347/347
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 12/12
- Rule coverage: 0 errors / 0 warnings
- Card catalog: 56 cards

Datacube: `MTGSim-rev0180-2026.07.08.04.54-preventionchoiceaudit.zip`
