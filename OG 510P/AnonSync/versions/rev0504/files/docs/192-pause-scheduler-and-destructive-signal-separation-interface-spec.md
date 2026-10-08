# Pause scheduler and destructive-signal separation interface spec

## Purpose

The archive already had convergence windows, route truth, and byte-witness guardrails.
What it still lacked was one interface contract for a deceptively familiar control:

> when the product says a share is `paused`, what page proves which classes of change are actually stopped, which still propagate, and whether the pause is about bandwidth, byte movement, deletion semantics, indexing, or all of the above?

Current official Resilio docs make this seam more concrete than a generic `pause is partial` aside would.
They still say pause and scheduled `Paused` cells stop upload/download bits, but zero-sized files and deletions still sync, new files are still rescanned and indexed, share size can keep increasing, and in the scheduler case a paused peer may still upload to non-paused peers while not downloading itself.

That is a good example of why AnonSync should not clone familiar labels without stronger public semantics.

## Core decision

AnonSync should split **transfer pause** from **destructive-signal flow** and **indexing posture**.

Every pause-like control must always declare:

- whether bytes are moving outbound
- whether bytes are moving inbound
- whether deletes still propagate
- whether namespace/indexing still advances
- whether local discovery continues
- whether the control is manual, scheduled, inherited, or emergency

If an operator still has to learn that `paused` allows deletions through by reading a help article after the fact, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- `paused` is overloaded across bandwidth, download, upload, delete, and indexing semantics
- scheduler pause and manual pause do not read like policy matrices even though they behave like them
- destructive propagation deserves its own control language rather than piggybacking on transfer language
- discovery/indexing may continue even when the operator thinks the subject is frozen
- a subject can become semantically newer while appearing operationally paused
- labels that sound absolute but behave selectively create the worst kind of surprise

AnonSync should therefore keep one stronger rule:

> pause-like controls must publish a matrix of allowed signal classes, not a single overloaded adjective.

## Fixed review order

Every pause, resume, or schedule rule should render the same sections in the same order:

1. **Signal matrix now**
2. **Origin and duration**
3. **Consequence review**
4. **Pause receipt**

### 1) Signal matrix now

This section should show:

- outbound bytes (`allowed`, `blocked`, `limited`)
- inbound bytes (`allowed`, `blocked`, `limited`)
- deletions (`allowed`, `blocked`, `reviewed`)
- namespace/indexing (`allowed`, `blocked`, `limited`)
- discovery/watcher activity (`allowed`, `blocked`, `limited`)

The operator must be able to answer: **what exactly is paused?**

### 2) Origin and duration

This section should show:

- whether the posture is manual, scheduled, inherited, or emergency
- when it started
- when it will end or be reconsidered
- whether it affects one subject, one bind, or the entire runtime

The operator must be able to answer: **who imposed this, and how long does it last?**

### 3) Consequence review

This section should show:

- whether deletes can still drain the subject
- whether namespace growth can continue
- whether overdue convergence is accumulating behind the pause
- whether peer-facing semantics differ from local expectations

The operator must be able to answer: **what can still change while this looks frozen?**

### 4) Pause receipt

This section should show only honest next actions, such as:

- `Block deletes too`
- `Keep discovery on but stop all bytes`
- `Freeze namespace and bytes`
- `Resume inbound only`
- `Schedule bandwidth limit instead of semantic pause`

The receipt must record the signal matrix before and after.

## Public objects

### Pause signal matrix

Fields:

- `pause_signal_matrix_id`
- `subject_ref` nullable
- `scope` (`subject`, `bind`, `runtime`)
- `origin` (`manual`, `scheduled`, `inherited`, `emergency`)
- `outbound_bytes`
- `inbound_bytes`
- `deletions`
- `namespace_indexing`
- `discovery`
- `starts_at`
- `ends_at` nullable

### Pause consequence review

Fields:

- `pause_consequence_review_id`
- `matrix_ref`
- `requested_action` (`tighten`, `loosen`, `resume`, `replace-with-bandwidth-limit`, `freeze-destructive-signals`)
- `expected_effects[]`
- `risks[]`
- `generated_at`
- `expires_at` nullable

### Pause receipt

Fields:

- `pause_receipt_id`
- `review_ref`
- `pre_matrix`
- `post_matrix`
- `completed_at`

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. scope
2. pause origin
3. byte posture
4. delete/index posture
5. next honest action

Example:

```text
subject/photos     scheduled     down blocked / up limited     deletes allowed / indexing allowed     Freeze destructive signals too
```

The product should not reduce that to `Paused` when the semantics are clearly a matrix.

## CLI implications

A minimum public surface should include:

```text
anonsync pause show --subject <subject>
anonsync pause plan --subject <subject> --action <action>
anonsync pause apply <pause_consequence_review_id>
anonsync pause receipt show <pause_receipt_id>
anonsync schedule show
```

The CLI should let an operator prove which signals still move before they trust a pause to be safe.
