# Recovery material attestation page: key, continuity, and drill status interface spec

## Purpose

`489` specifies the semantic truth of decrypt recovery.
What still remained was one page that forces the operator to prove preparedness *before* an incident, not reconstruct it during one.

This page exists to answer one ordinary operator question:

> if I am relying on this encrypted-custody node as part of my resilience story, what exact materials have I preserved, what exact continuity still survives, and how confident should I be that recovery will really work later?

## Core decision

Every encrypted-custody subject family must expose one first-class **Recovery material attestation** page.
That page is the semantic home of:

- key-material posture
- continuity posture
- drill / rehearsal posture
- effective recovery rung
- attestation receipts and expiry

The product must not treat `remember to save the key` as out-of-band lore.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. recovery-rung verdict strip
2. key-material card
3. continuity card
4. rehearsal and drill-status card
5. admissible next actions
6. attestation receipts

### 1) Recovery-rung verdict strip

Show one effective rung:

- `live peer recovery available`
- `encrypted-node recovery prepared`
- `encrypted-node recovery plausible but unproven`
- `cli/offline decrypt only`
- `recovery not currently defensible`

Also show:

- subject family
- custody seat in scope
- strongest missing proof
- next safest action

The operator must be able to answer: **what is my best honest recovery route right now?**

### 2) Key-material card

Show:

- RW key posture (`present`, `missing`, `suspected only`, `sealed`, `unknown`)
- RO key posture when relevant
- where the product knows those materials are governed
- whether location proof is direct, imported, or operator-attested only
- whether current roster / role policy still permits access

The page must not display secrets casually.
It should display proof of governance, not the key itself.

The operator must be able to answer: **do we truly have the materials required for recovery, or are we relying on memory?**

### 3) Continuity card

Show:

- whether the custody subject remains the same continuity-bearing instance
- whether the encrypted folder was ever removed/recreated
- whether database continuity is direct, inferred, uncertain, or broken
- whether target-path moves changed meaning
- strongest continuity threat

Possible verdicts:

- `continuity intact`
- `continuity likely intact`
- `continuity uncertain`
- `continuity broken`

The operator must be able to answer: **would recovery from this custody seat still be based on the same lineage, or did we quietly destroy the prerequisites?**

### 4) Rehearsal and drill-status card

Show:

- last rehearsal date
- rehearsal kind (`receipt-only`, `dry-run`, `local decrypt proof`, `live fetch proof`, `none`)
- result status
- time budget or operator burden
- whether another rehearsal is overdue

The product must strongly prefer rehearsal over narrative confidence.

The operator must be able to answer: **have we ever actually proved that this recovery story works?**

### 5) Admissible next actions

Typical actions:

- `Record governed key proof`
- `Review continuity evidence`
- `Schedule drill`
- `Run dry-run verification`
- `Escalate to manual recovery packet`
- `Downgrade resilience claim`

The page must not offer a cheerful `Looks good` path when proof is missing.

### 6) Attestation receipts

Each receipt must preserve:

- subject family
- custody seat
- effective recovery rung at the time
- key-material verdict
- continuity verdict
- rehearsal verdict
- actor and timestamp
- review horizon or expiry

This lets later reviewers answer: **what exactly was attested, by whom, and when does that attestation go stale?**

## Compact attestation row contract

A trustworthy compact row should preserve:

1. effective recovery rung
2. key-material verdict
3. continuity verdict
4. rehearsal verdict
5. next honest action

Example:

- `Encrypted-node recovery plausible but unproven · RW governed / RO unknown · Continuity likely intact · No drill yet · Schedule dry-run`

## Acceptance criteria

This spec is satisfied when:

- every resilience claim tied to encrypted custody can be backed by a current attestation
- secret-presence proof is separated from secret disclosure
- continuity loss is visible as a first-class downgrade
- recovery confidence can decay over time instead of staying permanently green after one remembered setup
