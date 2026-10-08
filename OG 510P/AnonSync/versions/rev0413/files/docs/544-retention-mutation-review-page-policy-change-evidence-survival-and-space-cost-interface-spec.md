# Retention mutation review page: policy change, evidence survival, and space cost interface spec

## Purpose

This page answers one ordinary operator question:

> if I change recovery retention, disable version capture, prune hidden stores, or make cleanup more aggressive, what future recovery truth am I destroying or preserving?

The page exists because retention is not a mere preference knob.
It is a mutation to the future proof surface of the product.

## Core decision

Every product that stores recovery witnesses must own one first-class **Retention mutation review** page.
That page owns:

- requested retention or capture change
- current and future evidence horizon delta
- size / space tradeoff
- residue implications
- safe language before apply
- durable record after apply

The operator must not weaken recovery truth through a small settings edit whose real effect is only documented elsewhere.

## Page layout

The page always renders the same regions in the same order:

1. requested-mutation strip
2. current-vs-future horizon compare
3. evidence-loss matrix
4. space-and-residue card
5. stronger-language veto card
6. apply summary
7. prior retention receipts

### 1) Requested-mutation strip

Show:

- requested change (`raise-ttl`, `lower-ttl`, `disable-versioning`, `change-size-ceiling`, `prune-hidden-store`, `cleanup-after-uninstall`, `preserve-forever`)
- scope (`subject`, `share`, `seat`, `fleet`, `unknown`)
- strongest immediate effect
- required review tier

### 2) Current-vs-future horizon compare

Show side-by-side:

- current byte-witness horizon
- current event-witness join quality
- future byte-witness horizon after apply
- future exclusions and cliffs after apply
- whether existing witnesses remain grandfathered, are pruned, or become inaccessible

### 3) Evidence-loss matrix

Rows represent affected witness classes.
Columns show:

- present state
- post-change state
- destroyed / narrowed / unchanged classification
- stronger claim lost
- reversibility

### 4) Space-and-residue card

Show:

- estimated storage relief or storage growth
- whether hidden control storage remains after app removal
- whether the change reduces only UI reach or actual on-disk residue
- whether a safer manual preservation step should occur first

### 5) Stronger-language veto card

Show explicit sentences the product forbids after apply, for example:

- `We still keep prior versions for this class.`
- `Uninstall clears all recovery residue.`
- `This history can always be recovered later.`
- `Lowering retention only affects old clutter, not real rollback ability.`

### 6) Apply summary

Show only the strongest honest apply sentence, for example:

- `Future byte witnesses on mobile will expire much sooner.`
- `Large files above the new ceiling will no longer generate version witnesses.`
- `Cleanup will remove hidden archive residue from this seat and permanently narrow later recovery options.`

## Non-negotiable rules

### Rule 1 — retention changes are proof-surface mutations

They may not be rendered as harmless cosmetic preferences.

### Rule 2 — future loss must be concrete

The product must say what witness class and what sentence are lost, not merely that `recovery may be affected`.

### Rule 3 — uninstall cleanup must stay explicit

If app removal does not erase hidden witness residue unless an extra cleanup step is taken, the review must name that difference.

## Honest outputs

The page may conclude:

- `Lowering retention will not erase current exported receipts, but future prior-version witnesses on this seat will disappear after a much shorter interval.`
- `Raising the size ceiling increases storage cost and extends recoverability only for large objects that are currently excluded from version capture.`
- `Cleanup after uninstall will remove hidden residual archive bytes and permanently narrow later forensic recovery from this seat.`
