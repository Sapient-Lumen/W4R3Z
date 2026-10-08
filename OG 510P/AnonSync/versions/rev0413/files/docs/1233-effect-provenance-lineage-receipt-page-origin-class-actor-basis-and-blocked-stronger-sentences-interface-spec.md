# Effect-provenance lineage receipt page — origin class, actor basis, and blocked stronger sentences

## Purpose

Persist one durable receipt for a surprising-state judgment so later operators do not have to reconstruct whether a state was directly authored, automatically healed, inherited, manually replayed, or merely re-noticed.

## Receipt questions

The receipt must answer:

1. What result class was judged?
2. What origin class won?
3. What actor basis or derivation basis supported that judgment?
4. What mechanism class explained the effect?
5. What stronger sentence was still blocked?

## Required fields

- `receipt_id`
- `target_ref`
- `result_class`
- `origin_class`
- `actor_basis`
- `mechanism_class`
- `publication_authority`
- `proof_class`
- `confidence_class`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `supersedes_receipt_id` nullable
- `created_at`

## Receipt body

### A. Summary line

The first line must read like one of these:

- `source-heal origin judged · actor basis = automatic runtime / standing policy`
- `manual archive replay judged · shared publish still not proven`
- `derived-source cascade judged · direct actor sentence blocked`
- `detection induction judged · new-content sentence blocked`

### B. Basis section

Show the minimum evidence that supported the verdict:

- posture / role evidence
- derivation evidence
- manual act evidence
- runtime witness evidence
- contradiction summary

### C. Non-equivalences preserved

The receipt must explicitly preserve which equivalence was refused, such as:

- `noticed now` ≠ `authored now`
- `restored` ≠ `manually recovered`
- `current bytes match source` ≠ `direct remote publish proven`
- `seat followed source` ≠ `named user chose this result`

### D. Reopen conditions

Show what later observations reopen the receipt:

- posture change
- manual replay after prior auto-heal verdict
- later direct publish witness
- derived-source break or re-parenting
- contradiction between timeline and current branch

## Design test

The product fails this receipt if a later operator can still say `I know what happened to the file, but I cannot tell whether that came from a person, a standing policy, an inherited seat, or a repair ritual.`
