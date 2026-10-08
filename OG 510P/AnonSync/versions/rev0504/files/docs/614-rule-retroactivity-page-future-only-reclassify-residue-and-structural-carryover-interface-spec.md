# Rule retroactivity page — future-only, reclassify, residue, and structural-carryover interface spec

## Purpose

The archive already has recovery and residue work.
What it still lacked was one ordinary page for the rule-timing question:

> if I add or change this exclusion rule now, what changes immediately, what stays because of prior sync history, and what residue still matters?

## Core decision

AnonSync must expose one first-class **Rule retroactivity** page for any rule whose effect on already-synced material can be mistaken for full reclassification.

## Fixed page order

1. **Timing class**
2. **Future intake effects**
3. **Already-synced residue**
4. **Structural carryover and claim ceiling**
5. **Action routing**

### 1) Timing class

Show each rule mutation split into its own timing family.
Example classes:

- future-only
- future + counting only
- future + visibility only
- requires reclassify action
- blocked by prior sync residue
- unknown

### 2) Future intake effects

Show:

- what new arrivals will do
- whether matching material will still be announced, indexed, counted, or transferred
- whether later rule alignment would change those behaviors

### 3) Already-synced residue

Show:

- matching items already present
- whether they remain counted, visible, searchable, or reachable
- whether disconnect or deeper cleanup is required to change the practical world

### 4) Structural carryover and claim ceiling

Show:

- structural metadata or tree information that still remains relevant
- strongest safe sentence
- stronger forbidden sentence
- which deeper page would provide the missing proof

### 5) Action routing

Actions may include:

- `Open cleanup intent review`
- `Open bind outcome review`
- `Open drift-class review`
- `Open rule agreement`
- `Copy safe sentence`

## Public object

### Rule retroactivity page

Fields:

- `rule_retroactivity_page_id`
- `rule_ref`
- `timing_class`
- `future_effect_rows[]`
- `residue_rows[]`
- `structural_carryover_rows[]`
- `claim_ceiling`
- `next_pages[]`
- `generated_at`
