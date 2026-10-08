# Service promotion contract sheet page — interactive seat, service seat, principal, and continuity class

## Purpose

Show, in one durable place before or immediately after cutover, what service transition is being requested and what continuity class currently applies.

This page exists to answer:

- `am I promoting the same seat into service life, or starting a different branch?`
- `which principal will run the service seat?`
- `what storage world is expected to back it?`
- `what observation and exposure deltas are already known?`
- `what stronger continuity sentence is blocked right now?`

## Required sections

### 1. Cutover header

Must show:

- cutover review id
- source runtime class (`interactive-desktop`, `interactive-headless`, `existing-service`, `unknown`)
- target runtime class (`service-current-user`, `service-local-service`, `service-local-system`, `service-other`, `unknown`)
- requested intent (`promote-same-seat`, `start-clean-service-branch`, `inspect-only`, `repair-existing-service`, `unknown`)
- current continuity class (`same-seat`, `same-seat-with-followup`, `clean-branch`, `different-storage-world`, `blocked`, `unknown`)

### 2. Source/target seat matrix

Must show separate rows for:

- runtime principal
- storage root
- visible roster basis
- mapped-path class
- notification grade
- control endpoint audience

Each row must publish:

- source value
- target value
- delta class (`same`, `widened`, `narrowed`, `different`, `unknown`)
- proof basis
- whether the row supports or weakens same-seat continuity

### 3. Continuity verdict block

Must distinguish at least:

- `same seat proven`
- `same seat likely; reconnect follow-up remains`
- `clean branch by operator choice`
- `different storage world opened`
- `blocked until cutover risk reviewed`
- `unknown; insufficient proof`

This block must answer:

> what exact kind of service transition is this, and what sentence about continuity is still honest now?

### 4. Migration basis block

Must show:

- whether install path says `migrate settings` or `clean installation`
- whether migrated roster has been witnessed yet
- whether empty state is expected, suspicious, or explained by a different storage world
- whether reconnect / re-share obligations already exist

### 5. Observation and exposure block

Must show:

- mapped-drive availability grade
- file-notification grade
- rescan dependence
- listener posture (`loopback-only`, `selected-interface`, `all-interfaces`, `none`, `unknown`)
- restart required for new exposure or policy

### 6. Strongest safe sentence

Examples:

- `This cutover promotes the same reviewed seat into service runtime under the same user-backed storage world.`
- `This cutover widens filesystem reach but opens a different storage world, so same-seat continuity is not proven.`
- `This is a clean service branch and requires reviewed reconnect of subjects.`

The page must also show one blocked stronger sentence, such as:

- `All prior shares are preserved automatically.`
- `Running as Local System continues the same seat.`
- `Browser-open proves the same node survived.`

## Required actions

- `Review principal switch`
- `Open service world preview`
- `Proceed to service cutover proof`
- `Abort cutover and keep interactive seat`
- `Export service lineage receipt`

## Guardrails

- Never let `service enabled` stand in for continuity class.
- Never collapse principal change into a purely permissions-shaped explanation.
- Never treat empty roster as silent absence; it must receive an attribution verdict.
- Never hide observation-grade downgrade inside a footnote.

## Output

A single contract sheet that makes service cutover legible enough that the operator no longer has to infer continuity from installer mood, browser-open, or troubleshooting lore.
