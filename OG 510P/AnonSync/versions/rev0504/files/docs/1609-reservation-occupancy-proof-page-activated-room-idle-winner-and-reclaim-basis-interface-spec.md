# Reservation occupancy proof page — activated room, idle winner, and reclaim basis

## Purpose

This page is the durable proof object for the strongest true sentence about awarded room after arbitration.
It exists so the archive can say exactly whether the winner activated and consumed the room, idly held it, or lost it back to reclaim.

## Sentences this page may support

- `room awarded but not yet activated`
- `room activated and productively consumed`
- `room activated but currently no-net-progress`
- `winner is idly holding awarded room`
- `award downgraded pending activation`
- `room reclaimed and claimant protection withdrawn`
- `contention reopened because activation failed`

## Mandatory proof blocks

### A. Award basis

- winning-claim reference
- award class
- protected-reserve exception flag
- loser set reference

### B. Activation evidence

- first activation witness
- productive-consumption witness
- last net-advance witness
- blocker witness if any
- idle-duration basis

### C. Reclaim or downgrade basis

- expired activation window yes/no
- starvation guard tripped yes/no
- reserve exception overrun yes/no
- blocker severity class
- reclaim approver if required

### D. Stronger blocked sentences

- strongest blocked sentence for the winner
- strongest blocked sentence for losing claimants
- exact fact needed to upgrade either sentence

## Required badges

- `awarded`
- `activated`
- `productive`
- `idle-held`
- `downgraded`
- `reclaimed`
- `reopened`

Badges must stack rather than overwrite lineage when later truth weakens or strengthens.

## Proof obligations

- prove activation separately from award
- prove productive occupancy separately from activation
- prove reclaim separately from expiry clock passage
- preserve loser blockage explicitly until reclaim or reallocation occurs
- preserve reserve-exception basis if protected reserve was borrowed

## Stronger-sentence guard

This page may say `winner had the room`.
It may not say `winner justified continuing exclusivity` unless the current state is productively consuming or a typed tolerated blocker still preserves that stronger sentence.