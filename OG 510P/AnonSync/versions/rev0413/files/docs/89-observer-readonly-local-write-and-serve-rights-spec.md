# Observer, read-only, local-write, and serve-rights spec

The archive already has share authority, grant mutation, retained-copy honesty, semantic fallback, selective materialization, and local-derivation review.
This document answers a narrower seam those abstractions still leave too loose:

> what must a real operator surface literally show when a subject is `read only`, `observer`, `viewer`, or `receive only`, so AnonSync never implies that one label alone answers what bytes are visible, what happens to local edits, whether that replica may serve data onward, and which projection or share-class limits still apply?

This is the access-posture companion to `74-authority-mutation-and-grant-boundary-review-spec.md`, the deviation companion to `44-file-intent-deviation-and-restore-spec.md`, the semantic-fallback companion to `86-semantic-fallback-and-optimization-review-spec.md`, and the retained-byte companion to `87-revocation-recall-and-retained-copy-attestation-spec.md`.

## Why this needs its own spec

Resilio's current docs still make this seam unusually clear.
`Is one-way synchronization possible?` says read-only peers can read data and receive full sync, but if they add, delete, or modify files those changes are not propagated and synchronization for the changed file is stopped.
`Folder Preferences` then says an `Overwrite any changed files` option can instead revert local changes on a read-only share, but that option is disabled when Selective Sync is on.
`User Management` says all linked devices under one identity act as Owners, while `How to create a Read Only folder while syncing across linked devices?` says linked-device read-only requires dropping to a Standard-folder/read-only-key ritual.
`Sharing a folder locally` adds that local shares inherit only the source share's permissions, cannot receive Owner, and in some Advanced-folder cases require remove-and-re-share to change local-share access.

That is useful support knowledge.
It is not yet one observer/rights contract.

The practical consequence is that several different truths still blur together too easily:

- the replica may see names only, placeholders, or full bytes
- local writes may be blocked, allowed but suspended, or allowed and auto-reverted
- the replica may or may not be allowed to serve clean bytes onward to others
- a permission label may apply only in some share classes or may require a weaker ritual to obtain
- selective-materialization and read-only repair may interact in ways that silently remove a remediation option
- an `observer`-like local projection may actually be a writable or authority-bearing participant under the hood

If the operator still has to remember that one `read only` case means `local edits stall sync`, another means `local edits are auto-overwritten`, another is unavailable for linked Advanced folders, and a local derivative may inherit only some of those semantics, the interface is not explicit enough.

## Core rule

AnonSync should treat observer-style access as a **bundle of four independently inspectable facts**, not one mode bit:

- **byte visibility posture** — names only, placeholders, or full bytes
- **local write posture** — blocked, tolerated-but-nonpropagating, auto-reverted, or review-required
- **onward serve posture** — may not serve, may serve clean bytes only, or may serve normally
- **projection and share-class limits** — what part of the posture exists only because of local projection, authority class, derivative shape, or runtime limitations

The product may compress low-risk cases.
It may not let `observer`, `read only`, `receive only`, `viewer`, or `on-demand` imply one stable behavior unless those four facts really line up that way.

## Vocabulary

### Observer posture contract

A durable summary of what a replica or local projection may see, write locally, serve onward, and repair automatically.

### Local write posture

The exact reviewed consequence of local file edits at a non-authoritative replica.
Examples: `writes-blocked`, `writes-suspend-path`, `writes-auto-reverted`, `writes-allowed-review-required`.

### Onward serve posture

The exact reviewed consequence for serving data from this replica to others.
Examples: `no-serve`, `serve-clean-bytes-only`, `serve-per-normal-authority`, `unknown-due-to-degraded-observation`.

### Projection and class boundary

The explicit statement of whether the observed posture comes from share authority, a local derivative/projection, selective-materialization mode, share class, or platform/runtime limitation.

### Observer-rights review

A reviewed case where the operator changes, narrows, inspects, or repairs observer-style access and needs the product to say what bytes are visible, what local writes do, what onward serving is allowed, and what limits still apply.

### Observer-rights receipt

A durable record proving which posture was accepted, repaired, narrowed, or refused, and what exact write/serve/projection facts were in force.

## Fixed review order

Every non-trivial observer/read-only/rights case should render the same sections in the same order:

1. **Requested access posture**
2. **Byte visibility and materialization reality**
3. **Local write and repair behavior**
4. **Onward serving and redistribution posture**
5. **Projection, share-class, and runtime limits**
6. **Receipt promise**

### 1) Requested access posture

This section should show:

- share, mount, derivative, or replica in scope
- whether the operator is creating observer access, narrowing existing writable access, repairing a broken read-only posture, or inspecting only
- the requested posture (`names-only observer`, `placeholder observer`, `full-byte observer`, `non-serving mirror`, `inspect-only`)
- whether the request is share-authority change, local projection change, or both

The operator must be able to answer: **what access shape is being requested, and is this really an authority change, a local projection change, or a mix?**

### 2) Byte visibility and materialization reality

This section should show:

- whether the subject currently sees names only, placeholders, or full bytes
- whether selective materialization or local derivatives are shaping what is visible
- whether the requested posture would fetch more bytes, evict bytes, or leave current materialization intact
- whether the strongest honest statement is `observer-by-placeholder`, `observer-by-full-copy`, or `observer-by-local-derivative`

The operator must be able to answer: **what bytes or names are actually visible here right now, and what would change locally if I apply this?**

### 3) Local write and repair behavior

This section should show:

- whether local writes are blocked at the source, tolerated but will suspend that path, auto-reverted, or escalated into reviewed deviation handling
- whether any overwrite/revert helper is available, unavailable, or disabled by projection mode
- whether added local files remain local residue, become explicit deviations, or are disallowed outright
- whether repair is path-scoped, subtree-scoped, or requires a wider review because the current posture is inconsistent

The operator must be able to answer: **if someone edits a file here anyway, what exactly happens next?**

### 4) Onward serving and redistribution posture

This section should show:

- whether this subject may serve clean bytes onward to peers, may not serve at all, or inherits ordinary serve rights
- whether serve behavior comes from authority, derivative shape, cache state, or degraded observation
- whether retained local bytes may still matter for reseed even when local writes are non-authoritative
- whether the request narrows future service, narrows only local write authority, or does both

The operator must be able to answer: **can this replica help other peers, and if so under what exact limits?**

### 5) Projection, share-class, and runtime limits

This section should show:

- whether this posture exists only for a certain share class, derivative shape, runtime seat, or client/platform projection
- whether linked-constellation convenience would silently widen the same subject back to owner-like or writable behavior elsewhere
- whether local-share or derived-posture changes can mutate in place or require rebuild/reissue
- whether the requested observer mode is blocked, degraded, or only emulable through a weaker class/ritual

The operator must be able to answer: **which parts of this posture are fundamental rights and which parts are artifacts of class, projection, or platform limits?**

### 6) Receipt promise

This section should show:

- which observer-rights receipt will exist after apply, defer, or refusal
- what it will later prove about visible bytes, local-write posture, onward serving, and limiting conditions
- whether later authority rotation, recall, or derivation follow-up is still required for a stronger claim
- where the same review survives if the operator continues in another channel

The operator must be able to answer: **what later evidence will prove exactly what this supposedly read-only or observer replica could and could not do?**

## Public objects

### Observer posture contract

Fields:

- `observer_posture_contract_id`
- `subject_ref`
- `subject_kind` (`share-peer`, `mount`, `local-derivative`, `replica`, `incoming-claim`)
- `byte_visibility_posture` (`names-only`, `placeholder-visible`, `full-bytes-visible`, `mixed-materialization`)
- `local_write_posture` (`writes-blocked`, `writes-suspend-path`, `writes-auto-reverted`, `writes-allowed-review-required`)
- `onward_serve_posture` (`no-serve`, `serve-clean-bytes-only`, `serve-per-normal-authority`, `unknown-due-to-degraded-observation`)
- `projection_limit_posture` (`none`, `share-class-bound`, `selective-sync-bound`, `derivative-bound`, `runtime-bound`, `client-bound`)
- `authority_source` (`share-grant`, `local-projection`, `derived-local-share`, `legacy-import`, `unknown`)
- `repair_mode` (`none`, `path-revert`, `subtree-repair`, `review-required`, `unavailable`)
- `current_materialization_summary`
- `serve_reseed_summary`
- `generated_at`
- `expires_at` nullable

### Observer-rights review

Fields:

- `observer_rights_review_id`
- `subject_ref`
- `requested_posture` (`names-only-observer`, `placeholder-observer`, `full-byte-observer`, `non-serving-mirror`, `inspect-only`)
- `requested_change_class` (`narrow-authority`, `change-local-projection`, `repair-readonly-posture`, `inspect-only`)
- `current_contract_ref`
- `byte_visibility_findings[]`
- `local_write_findings[]`
- `serve_posture_findings[]`
- `projection_limit_findings[]`
- `follow_on_review_refs[]`
- `action_options[]`
- `observer_rights_report_ref`
- `generated_at`
- `expires_at` nullable

### Observer-rights receipt

Fields:

- `observer_rights_receipt_id`
- `review_ref`
- `subject_ref`
- `accepted_posture_summary`
- `byte_visibility_summary`
- `local_write_summary`
- `serve_posture_summary`
- `projection_limit_summary`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable

## Public rules

1. **Read-only is not one fact.**
   Byte visibility, local-write behavior, onward serving, and projection limits must stay separately inspectable.

2. **Local write repair must stay explicit.**
   The product must not hide whether local edits stall sync, auto-revert, or become review-worthy deviations.

3. **Projection limits must not masquerade as authority truth.**
   If a posture exists only because of selective materialization, local derivation, client limits, or weaker share class, that constraint must stay visible.

4. **Observer replicas may still matter operationally.**
   A non-authoritative or read-only replica may still hold bytes that matter for reseed, recall, or settlement, so `cannot write` must not imply `operationally irrelevant`.

5. **Linked-convenience widening must stay obvious.**
   If a convenience constellation or same-identity projection would upgrade the same subject to owner-like or writable participation elsewhere, the review must say so.

6. **Receipts must prove the exact bundle.**
   Future audit must be able to show not just that a subject was `read only`, but what that meant for bytes, writes, serve rights, and boundary limits.

## CLI surface

```text
anonsync observer show --subject shp_01J...
anonsync observer show --mount mnt_01J...
anonsync observer prepare --share reports --peer dev_tablet --posture full-byte-observer --plan
anonsync observer prepare --derivative ldr_01J... --posture placeholder-observer --change change-local-projection --plan
anonsync observer repair --subject shp_01J... --mode path-revert --plan
anonsync observer review show orr_01J...
anonsync observer apply orr_01J...
anonsync observer receipt show orc_01J...
```

The group should answer:

- what the subject can currently see and whether that means placeholders or full bytes
- what a local edit would do right now
- whether the subject may serve bytes onward or only consume them
- which parts of that posture come from authority versus local projection or share-class/runtime limits
- which receipt later proves the exact observer bundle rather than a vague `read only` label
