# Concurrent edit review page — online sequence, offline return, delay mitigation, and loser placement

## Purpose

Review a concrete same-path multi-edit event before the interface states who won.
This page exists because `file changed in two places` is not one situation.

## This review must distinguish

- two or more peers editing while online and mutually visible
- one peer editing offline and later returning
- edits arriving while clocks are outside the allowed trust window
- lock-prone or app-prone workflows where file-class delay should be recommended for future runs
- name/path conflicts versus content chronology conflicts

## Inputs the page must collect

### Peer and presence facts

- peers involved
- whether each peer was online or offline during each edit
- whether any peer rejoined after a local offline edit
- whether change notifications were observed, missed, or manually induced

### Time facts

- local file mtime
- remote file mtime
- UTC-normalized peer-time delta
- whether the delta is within the allowed window
- whether time-zone mismatch or clock drift is suspected

### Detection / mitigation facts

- was a `touch` or rescan used
- is `ignore_mtime_assign_errors` active or suspected relevant
- is a file-class delay configured for this extension or file kind
- was the file edited by a conflict-prone application family

## Decision ladder

### Branch 1 — online ordered progression

Use this branch when all relevant peers were online and time authority is trusted.
The page should show:

- sequence of observed edits
- currently winning version
- currently displaced versions
- survivor placement for displaced versions

### Branch 2 — offline-return winner

Use this branch when a peer returns after offline editing.
The page should show:

- that later online edits may still lose to the returning offline version under the current Resilio-style rule family being evaluated
- which versions were overwritten
- where those overwritten versions were placed
- that `offline-return winner` is a contract class, not an anomaly note

### Branch 3 — time-skew blocked

Use this branch when peer time drift or time-zone error exceeds the configured trust window.
The page should show:

- that transfer is blocked or chronology is untrustworthy
- which peers must fix time first
- whether mobile peers may show empty-list symptoms
- that no winner sentence is allowed yet

### Branch 4 — detection uncertainty

Use this branch when mtime or notifications did not move as expected.
The page should show:

- why detection may have missed the edit
- whether `touch` or rescan is the next honest proof step
- that no chronology verdict is final until re-observation completes

## Future-risk mitigation panel

The page must include a separate panel for future recurrence, not merged with the current verdict.
It must offer:

- `Enable or review file-class delay for this extension family`
- `Leave delay unchanged`
- `Do not recommend delay for this file class`

The panel must state that delay mitigation is about *future conflict risk* and does not retroactively prove the present winner.

## Required warnings

- `Later online work can still lose to a returning offline peer.`
- `Clock repair is required before chronology claims become trustworthy.`
- `Manual touch changes detection, not authorship.`
- `Archive placement preserves bytes, not correctness.`
- `Delay settings reduce conflict pressure but do not arbitrate current truth.`

## Review outputs

- winning version basis
- loser placement
- chronology certainty grade
- required remediation before stronger claims
- optional future delay recommendation

