# Bypass review page: pause, disconnect, network gate, and claim downgrade interface spec

## Purpose

The control-suspension contract carries the candidate override.
What the archive still needs before arming it is one comparison page answering:

> which kind of stop are we actually choosing, what cheaper or safer alternative exists, and what claim must be downgraded immediately if we proceed?

## Core decision

AnonSync must expose one first-class **Bypass review** whenever more than one stop-like action could plausibly satisfy the operator's request.

## Fixed page order

1. **Review header**
2. **Candidate-stop lattice**
3. **Semantic-difference card**
4. **Claim-downgrade comparison**
5. **Expiry and re-arm card**
6. **Approval sentence**

### 1) Review header

Show:

- target control id
- reason for bypass
- compared candidate classes
- selected candidate
- rejected stronger candidates
- rejected weaker candidates
- current recommendation

### 2) Candidate-stop lattice

Each row compares one candidate class.
Required columns:

- candidate class
- what actually stops
- what still survives
- scope
- reversibility
- risk of hidden side effects
- whether trust is auto-restored or not

Supported `candidate_class` values:

- `local-pause`
- `global-pause`
- `scheduled-pause-window`
- `network-gated-stop`
- `background-priority-drop`
- `disconnect-but-reconnectable`
- `peer-revocation`
- `remove-or-recreate`
- `scope-narrow-without-stop`

Hard rule:

Candidates may not be sorted by label familiarity; they must be sorted by least-destructive semantics first.

### 3) Semantic-difference card

This card highlights the easiest confusions.
Required rows:

- delete propagation difference
- upload/download asymmetry
- indexing/detection difference
- placeholder/path consequence
- relationship/topology consequence
- auto-resume difference

Supported `semantic_difference_flag` values:

- `looks-paused-but-still-propagates-deletes`
- `looks-paused-but-still-indexes`
- `looks-disconnected-but-path-persists`
- `looks-resumable-but-may-create-new-path`
- `looks-local-but-revokes-peer-updates`
- `looks-stopped-but-system-may-restart-it`

### 4) Claim-downgrade comparison

Required rows:

- sentence lost immediately for each candidate
- weakest surviving sentence
- stronger sentence still blocked after resume
- whether new attestation is required after resume
- effect on related recurrence watch or rollout gate

Hard rule:

A candidate that requires less operator work but causes a stronger trust downgrade must not be hidden.

### 5) Expiry and re-arm card

Required rows:

- expiry style
- who can extend
- mandatory check at expiry
- resume proof type
- when same-cause case or rollout reopens

Supported `expiry_style` values:

- `hard-expiry-auto-alert`
- `soft-expiry-needs-review`
- `schedule-bounded`
- `environment-bounded`
- `manual-only-no-auto-expiry`

### 6) Approval sentence

The page ends with one sentence in this shape:

> `We choose <candidate class> instead of <rejected alternative> because it suppresses <target effect> with lower semantic cost; while active it still allows <surviving effect> and therefore blocks <overclaim>.`
