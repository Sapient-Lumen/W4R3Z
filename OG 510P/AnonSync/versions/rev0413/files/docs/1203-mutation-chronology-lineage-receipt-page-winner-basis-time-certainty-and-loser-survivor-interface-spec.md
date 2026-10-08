# Mutation chronology lineage receipt page — winner basis, time certainty, and loser survivor

## Purpose

Preserve one durable receipt for any conflict, chronology dispute, or older-byte republish action.
Later operators must not have to reverse-engineer the winner from archives, mtimes, or memory.

## Receipt identity

- receipt id
- subject id
- path at review time
- review timestamp
- operator / actor
- event class (`online-order`, `offline-return`, `time-skew-block`, `manual-republish`, `detection-recompute`, `other`)

## Required recorded facts

### Chronology verdict

- `winner_class` (`online-latest-observed`, `offline-return-winner`, `blocked-no-winner`, `manual-republish-pending`, `manual-republish-observed`, `other`)
- `winner_basis[]`
- `time_authority_class`
- `proof_grade`

### Loser survivor map

- `loser_versions_present` (`yes`, `no`, `unknown`)
- `loser_location[]` (`local-archive`, `remote-archive`, `parked-copy`, `still-live-remote`, `unknown`)
- `archive_index_or_reference` when available

### Detection and remediation

- `detection_basis` (`filesystem-notify`, `mtime-change`, `manual-touch`, `rescan`, `mixed`, `unknown`)
- `delay_mitigation_posture` (`none`, `recommended`, `enabled`, `declined`, `not-applicable`)
- `runtime_witness_at_restore` (`live`, `not-live`, `uncertain`, `not-applicable`)

### Ceiling language

- `blocked_stronger_sentence`
- `next_proof_required`

## Receipt rendering rules

The human-readable receipt must say, in one compact paragraph:

- why this version won or why no winner was declared
- how trustworthy the time basis was
- where the losing bytes survived, if known
- what still had to happen before rollback or convergence could be claimed

## Example operator-facing sentence shapes

- `Returning offline peer won under current chronology policy; previous online version survived in local Archive; clock posture trusted; rollback not claimed.`
- `No chronology verdict issued because peer time exceeded allowed window; transfer blocked pending clock repair.`
- `Older archive version restored while runtime live; touch remediation required before convergence can be claimed.`

