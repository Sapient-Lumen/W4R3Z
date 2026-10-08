# Ghost announcement, byte-witness absence, and source-revival repair interface spec

## Purpose

The archive already had file availability, witness strength, and no-byte-horizon language.
What it still lacked was one interface contract for a narrower but very common failure:

> when the mesh remembers a file name or announcement but nobody can presently supply the bytes, what page says this is an **announcement-without-witness** problem instead of just `download failed`?

Current official Resilio docs make this seam much sharper than a generic offline-source error would.
They still describe a warning where a peer in Selective Sync announces a new or updated file, other peers merge the tree, and by the time they try to fetch the file the source has reverted it to a placeholder or removed the actual bytes.
The current docs explicitly call this a kind of `ghost file` case and still say that if the bytes no longer exist anywhere the warning can simply be ignored, but that operators should be careful because a more up-to-date version may still exist on an offline peer.
The documented repair for a definitely-correct local copy is still to `touch` the files or move them out of the shared folder and then back in to force re-announcement.

That is operationally useful.
It is not a clean public repair grammar.

## Core decision

AnonSync should separate **announced namespace state** from **byte witness state** everywhere.

A path, file, or subtree may therefore be:

- announced and fetchable
- announced but witness-weak
- announced but witness-absent
- hidden locally but byte-witnessed elsewhere
- locally present and byte-authoritative
- disputed because an offline witness may still hold the newer version

If a user still has to infer those distinctions from placeholder icons, peer availability, and whether `touch it` made the warning go away, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- the namespace can converge faster than byte availability
- placeholders and merged trees can make a file look more real than it is
- a source peer can announce bytes and later stop being a source for them
- ignoring the warning and resurrecting the file are both plausible actions, but they mean different things
- an offline peer can still be the most recent byte witness even when no online peer can prove it
- repair currently depends on ritual re-announcement instead of one explicit byte-authority review

AnonSync should therefore keep one stronger rule:

> every `cannot fetch` case must say whether the problem is transport, authority, or absent byte witnesses, and it must name the honest repair ladder.

## Fixed review order

Every non-trivial ghost-announcement case should render the same sections in the same order:

1. **Announcement and namespace state**
2. **Current byte witnesses**
3. **Authority and chronology uncertainty**
4. **Repair and receipt promise**

### 1) Announcement and namespace state

This section should show:

- the announced path exactly as known to the mesh
- who last announced it
- whether the local namespace shows a placeholder, ordinary entry, or nothing
- whether the current warning is file-level or subtree-level

The operator must be able to answer: **what is the mesh claiming exists?**

### 2) Current byte witnesses

This section should show:

- online byte witnesses
- offline byte witnesses
- placeholder-only holders
- stale or uncertain witnesses
- whether any local copy is complete and hash-verified

The operator must be able to answer: **who, if anyone, can actually serve bytes right now?**

### 3) Authority and chronology uncertainty

This section should show:

- whether an offline peer may hold the newest version
- whether the local copy may safely become the new announcer
- whether this is really a delete that has not converged yet
- whether waiting is stronger than forcing re-announcement

The operator must be able to answer: **am I missing bytes, or am I missing certainty about which bytes should win?**

### 4) Repair and receipt promise

This section should show only honest next actions, such as:

- `Wait for the newest offline witness`
- `Promote verified local bytes as new source`
- `Ignore stale announcement`
- `Pin a durable witness before clearing placeholders`
- `Escalate chronology dispute`

The receipt must record the witness set and chronology verdict used at apply time.

## Public objects

### Ghost announcement case

Fields:

- `ghost_announcement_case_id`
- `subject_ref`
- `path_ref`
- `last_announcer_ref` nullable
- `namespace_state` (`ordinary-entry`, `placeholder-only`, `hidden`, `mixed`)
- `witness_verdict` (`fetchable`, `weak`, `absent`, `disputed`)
- `online_witness_refs[]`
- `offline_witness_refs[]`
- `placeholder_only_refs[]`
- `generated_at`

### Byte-authority repair review

Fields:

- `byte_authority_repair_review_id`
- `case_ref`
- `requested_action` (`wait`, `promote-local`, `ignore-announcement`, `pin-witness`, `escalate`)
- `chronology_verdict` (`clear`, `uncertain`, `disputed`)
- `candidate_authority_ref` nullable
- `generated_at`
- `expires_at` nullable

### Byte-authority receipt

Fields:

- `byte_authority_receipt_id`
- `review_ref`
- `applied_action`
- `post_action_witness_verdict`
- `post_action_authority_ref` nullable
- `chronology_basis`
- `completed_at`

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. path
2. namespace state
3. byte witness verdict
4. chronology certainty
5. next honest action

Example:

```text
/Video/clip.mov     placeholder-only     absent     offline witness may be newer     Wait or promote verified local bytes
```

The product should not reduce that to `cannot download` and leave the operator to guess whether the file is gone, late, or merely unproven.

## CLI implications

A minimum public surface should include:

```text
anonsync ghost show --path <path>
anonsync ghost review <ghost_announcement_case_id> --action <action>
anonsync ghost apply <byte_authority_repair_review_id>
anonsync ghost receipt show <byte_authority_receipt_id>
anonsync witness show --path <path>
```

The CLI should let an operator answer `who has the bytes, who may have the newest bytes, and what can I safely do now?` without touching files just to provoke state.
