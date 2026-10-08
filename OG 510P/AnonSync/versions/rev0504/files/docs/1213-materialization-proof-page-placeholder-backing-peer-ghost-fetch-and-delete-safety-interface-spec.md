# Materialization proof page — placeholder backing peer, ghost fetch, and delete safety

## Purpose

After any serious `can I actually fetch this file?` or `what did this delete-like gesture really mean?` dispute, a later operator must be able to answer without reopening placeholder folklore.
This page exists because namespace visibility, byte backing, and destructive authority all weaken differently.

## Proof ladder

### Rung 1 — weak presence only

We know the object is named in the UI or namespace.
We do **not** yet know that local bytes exist or that any live peer can supply them.

Show:

- object identity
- current presence class
- no proven backing source yet
- no local-byte sufficiency proof yet

Allowed sentence:

- `object name is known, byte backing still weak`

Blocked stronger sentence:

- `the file is retrievable now`

### Rung 2 — placeholder with provisional source

We know the object is represented by placeholders and that a source is known historically or currently expected.
We do **not** yet know that a source peer is presently available with the bytes.

Show:

- placeholder evidence
- last known source identity or source class
- whether the source is online, offline, or unknown
- whether a parent share is itself placeholder-only

Allowed sentence:

- `placeholder present, source expectation provisional`

Blocked stronger sentence:

- `materialization will succeed now`

### Rung 3 — live materialization source proven

We know at least one eligible source currently has the bytes and is available for transfer.

Show:

- proven source count
- proof time
- transfer eligibility blockers, if any
- whether the materialization path still depends on remote state after local removal

Allowed sentence:

- `materialization source currently proven`

Blocked stronger sentence:

- `future fetch remains guaranteed after any local residency change`

### Rung 4 — ghost-fetch condition

We know the namespace or warning refers to a file that no currently proven peer actually has.

Show:

- ghost indicator
- last known announcement basis
- why current fetch is impossible
- remediation options such as explicit ignore, manual review, or source reappearance

Allowed sentence:

- `object remembered, byte source not currently proven anywhere`

Blocked stronger sentence:

- `waiting longer alone will restore the file`

### Rung 5 — delete-safety proof

We know what the reviewed gesture can and cannot destroy.

Show:

- gesture reviewed
- whether it changes only local residency or shared existence
- whether safety rails are disabling global delete from this surface
- archive or recovery consequence, if any

Allowed sentence:

- `gesture authority proven at reviewed blast radius`

Blocked stronger sentence:

- `delete wording here is harmless`

## Required side proofs

The page must also show:

- whether placeholders are protected by safety toggles
- whether source proof depends on linked-device topology rather than independent peers
- whether local bytes would remain self-sufficient after disconnect
- whether a reconnect would need manual path correction to reattach the intended namespace

## Compact output

The page must produce:

- `materialization_confidence` (`name_only`, `placeholder_provisional`, `source_proven`, `ghost`, `local_self_sufficient`)
- `source_proof_class` (`none`, `historical_only`, `live_remote`, `local_bytes`, `ghost`)
- `delete_safety_class` (`local_only`, `shared_destructive`, `blocked_by_policy`, `manual_review_required`)
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
