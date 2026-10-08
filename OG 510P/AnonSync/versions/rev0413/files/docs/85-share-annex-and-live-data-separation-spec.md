# Share-annex and live-data separation spec

The archive already has state roots, filesystem fidelity, target custody, storage budgets, projection policy, and rollback history.
This document answers a narrower seam those abstractions still left too loose:

> what must a real operator surface literally show when sync needs share identity markers, ignore/projection policy, archive/history bytes, xattr carry-forward state, or in-flight transfer residue, so AnonSync does not smear control meaning into the user's ordinary data tree as hidden magic?

This is the share-layout companion to `42-state-root-and-service-profile-spec.md`, the namespace companion to `46-namespace-projection-and-placeholder-spec.md`, the rollback-storage companion to `48-history-conflict-and-rollback-provenance-spec.md`, the fidelity companion to `49-filesystem-portability-and-semantic-fidelity-spec.md`, the storage-budget companion to `51-space-pressure-reclaim-and-retention-budget-spec.md`, and the host-local-ownership companion to `81-target-custody-and-exclusive-bind-review-spec.md`.

## Why this needs its own spec

Resilio's docs make the seam uncomfortably concrete.
`What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` says each synced folder gets a hidden `.sync` directory that is critical for synchronization, contains the folder ID and service files, stores `Archive`, `IgnoreList`, and `StreamsList`, and leaves files ending in `.!sync` in the share while data is in flight.
`Ignoring files in Sync (Ignore List)` says `IgnoreList` itself lives inside hidden `.sync`, is case-sensitive, does not work for files that have already been synced, and that once structural information has been scanned and indexed it remains in the database and is passed to peers until the share is disconnected.
`Alt Streams and Xattrs in Sync` says xattrs are whitelisted through `.sync/StreamsList`, cannot be ignored through `IgnoreList`, and may spill into `.sync/Streams` stub files when the local filesystem cannot represent them directly.
`Using Archive for file versioning and restoring deleted files` says restore is manual and, outside desktop UI shortcuts, runs through the hidden `.sync/Archive` path itself.
`Service files missing / Cannot identify destination folder` says repair can still mean `make sure nothing important is in archive`, delete `.sync`, and add the share back.

That is useful support knowledge.
It is not yet one honest share-layout contract.

The practical consequence is that five different byte classes keep collapsing together:

- live user data
- share identity and policy state
- rollback/history retention bytes
- in-flight transfer residue
- metadata-carry artifacts used only because one filesystem cannot represent another faithfully

If the operator still has to infer which class a byte belongs to from hidden names, support articles, or `delete .sync and retry` ritual, the product is not explicit enough.

## Core rule

AnonSync should separate the ordinary live namespace from sync control/state bytes as a first-class public contract.
A share layout may be:

- ordinary live namespace with external annex
- ordinary live namespace with adjacent managed annex
- explicit in-tree managed area accepted by review
- imported legacy layout kept inspectable until migrated
- blocked / inspect-only

A layout may not silently treat required control markers, history stores, metadata stubs, or in-flight residue as though they were just more user files.
Likewise, cleanup may not silently destroy layout evidence just because the confusing bytes happen to be hidden.

## Which actions are in scope

This spec is about any action where live data and managed sync state could otherwise blur together.
That includes at least:

- creating a new share or adopting an incoming one
- choosing where share-control annex state lives
- deciding whether history/rollback bytes live alongside the share or in a separate managed store
- handling xattr or metadata portability with native support, explicit sidecars, or reviewed drop policy
- inspecting or cleaning temp/in-flight residue after partial download, interruption, or low-space events
- importing, preserving, or migrating a legacy share that already embeds control bytes in-tree
- deciding what, if anything, should be visible inside the ordinary mount path versus only in workbench/report surfaces

Low-risk layout inspection can stay lighter.
Any action that changes what bytes live inside the user tree cannot.

## Vocabulary

### Live namespace

The ordinary tree the subject treats as their files and folders.
This is the namespace file browsers, editors, media tools, and backup tooling should be able to interpret without also learning sync internals.

### Share annex

A managed location that stores share-control material which does not belong in the ordinary live namespace: share identity markers, policy snapshots, metadata-carry artifacts, temp-transfer residue, retention sidecars, or migration evidence.
The annex may be external, adjacent, or explicitly in-tree only by reviewed choice.

### Residue class

A named class of non-ordinary bytes associated with a share, such as `history`, `temp-transfer`, `metadata-carry`, `policy-mirror`, or `legacy-import`.
Residue classes exist so cleanup and space accounting do not flatten into `hidden files`.

### Layout review

A reviewed case that answers whether the current or requested share layout keeps ordinary files, managed control state, rollback bytes, and portability artifacts honestly separated.

### Layout receipt

A durable record proving what the layout was, what byte classes were exposed or relocated, and what cleanup or migration fallout was accepted.

## Fixed review order

Every non-trivial share-layout review should render the same sections in the same order:

1. **Requested share layout and visibility**
2. **Live namespace guarantee**
3. **Annex placement and metadata-carry posture**
4. **Residue, history, and cleanup posture**
5. **Admissible actions**
6. **Receipt promise**

### 1) Requested share layout and visibility

This section should show:

- current share, mount, and live-root path
- current layout class and requested layout class
- whether the current bytes reflect fresh AnonSync layout, imported legacy layout, or ambiguous foreign state
- requested visibility posture for managed bytes (`external-only`, `adjacent-managed`, `in-tree-explicit`, `inspect-only`)
- whether this is low-risk inspection, migration, cleanup, or high-signal layout mutation

The operator must be able to answer: **am I only inspecting layout, or am I about to change what kinds of bytes appear in the live tree?**

### 2) Live namespace guarantee

This section should show:

- which paths are promised to remain ordinary live files only
- whether any managed bytes are currently exposed in-tree and why
- whether live namespace semantics are clean, mixed, legacy-imported, or blocked
- whether file-browser-visible hidden entries remain part of the operator contract or only migration evidence

The operator must be able to answer: **which bytes in this path are truly mine, and which are only here because the product has not separated itself yet?**

### 3) Annex placement and metadata-carry posture

This section should show:

- where annex state lives now and where it would live after apply
- which byte classes are stored there (`identity-marker`, `policy-mirror`, `metadata-carry`, `temp-transfer`, `history`, `legacy-evidence`)
- whether xattr or metadata portability uses native representation, explicit annex sidecars, explicit in-tree sidecars, or reviewed drop-with-receipt
- whether layout migration would preserve, relocate, or retire existing in-tree managed bytes

The operator must be able to answer: **where does the sync system keep its own truth, and how does metadata portability avoid pretending service bytes are normal content?**

### 4) Residue, history, and cleanup posture

This section should show:

- whether rollback/history bytes are external, adjacent, explicit in-tree, disabled, or inherited from legacy import
- whether temp-transfer residue can appear in the live tree, only in annex, or in both with explanation
- what cleanup classes are safe, review-required, blocked, or preservation-sensitive
- whether prior hidden bytes are still needed for migration, audit, or recovery before cleanup

The operator must be able to answer: **what may I clean safely, what history would I lose, and which odd files are temp/control residue rather than user content?**

### 5) Admissible actions

This section should show:

- whether the honest next step is keep current layout, migrate to external annex, preserve and inspect legacy state, clean reviewed residue, or block
- which shortcuts are forbidden because they would destroy layout evidence or blur live data with managed state again
- whether the product can offer a safely compressed path because the live namespace is already clean and no preservation class is at risk
- what follow-up remains if the operator defers migration or cleanup

The operator must be able to answer: **what can I safely do right now without lying about which bytes are data versus sync machinery?**

### 6) Receipt promise

This section should show:

- which layout receipt will exist after apply, defer, or refusal
- what it will later prove about live namespace cleanliness, annex location, residue classes, and cleanup/migration fallout
- whether later cleanup still depends on a preservation checkpoint or settlement barrier
- where later audit survives if the action resumes from another channel

The operator must be able to answer: **what later evidence will prove that my share tree became cleaner — or prove that I knowingly kept legacy managed bytes in view?**

## Public objects

### Share layout contract

Fields:

- `share_layout_contract_id`
- `share_ref`
- `mount_ref` nullable
- `live_root_path`
- `live_namespace_state` (`clean`, `mixed-managed`, `legacy-import`, `inspect-only`, `blocked`)
- `layout_class` (`external-annex`, `adjacent-managed`, `in-tree-explicit`, `legacy-imported`, `unknown`)
- `annex_path` nullable
- `annex_visibility` (`not-mounted`, `managed-visible`, `in-tree-explicit`, `unknown`)
- `managed_byte_classes[]`
- `history_storage_class` (`external-annex`, `adjacent-managed`, `in-tree-explicit`, `disabled`, `legacy-import`)
- `temp_residue_policy` (`external-only`, `adjacent-managed`, `in-tree-explicit`, `mixed`, `unknown`)
- `metadata_carry_mode` (`native-only`, `annex-sidecar`, `in-tree-sidecar-explicit`, `drop-with-receipt`, `unknown`)
- `ignore_policy_ref` nullable
- `projection_policy_ref` nullable
- `cleanup_risk_state` (`none`, `review-required`, `preservation-required`, `blocked`, `unknown`)
- `last_verified_at`
- `provenance_ref` nullable

### Share layout review

Fields:

- `share_layout_review_id`
- `share_ref`
- `mount_ref` nullable
- `current_layout_contract_ref`
- `requested_layout_class` (`external-annex`, `adjacent-managed`, `in-tree-explicit`, `inspect-only`, `cleanup-only`)
- `requested_visibility_posture` (`external-only`, `adjacent-managed`, `in-tree-explicit`, `inspect-only`)
- `live_namespace_findings[]`
- `annex_findings[]`
- `residue_findings[]`
- `cleanup_requirements[]`
- `action_options[]`
- `share_layout_report_ref`
- `generated_at`
- `expires_at` nullable

### Layout receipt

Fields:

- `layout_receipt_id`
- `review_ref`
- `share_ref`
- `live_namespace_summary`
- `annex_summary`
- `residue_summary`
- `cleanup_summary`
- `actor_ref`
- `created_at`

## What the surface must never imply

The share-layout surface must never imply that these are the same thing:

- live user files versus control markers required for share identity
- rollback/history retention versus ordinary folders the operator created
- metadata-carry sidecars versus portable user-visible content
- in-flight temp residue versus completed user data
- editing ignore/projection policy versus physically cleaning old managed bytes
- `delete hidden folder` convenience versus safe reviewed reset

If the product compresses those differences, it has recreated the hidden-layout ritual it is trying to replace.

## CLI shape

Examples:

```text
anonsync layout show workdocs
anonsync layout show workdocs --mount mnt_01J...
anonsync layout compare workdocs --path ~/Sync/workdocs
anonsync layout prepare workdocs --annex /var/lib/anonsync/annex/workdocs --temp-residue external-only --history external-annex --plan
anonsync layout prepare workdocs --cleanup-class metadata-carry --plan
anonsync layout review show slr_01J...
anonsync layout apply slr_01J...
anonsync receipts show lyr_01J...
```

The point is not the exact spelling.
The point is that ordinary share browsing and explicit layout/control-state work remain visibly different verbs.

## Workbench shape

The workbench should expose a dedicated share-layout surface whenever a share contains imported legacy managed bytes, reviewed in-tree managed areas, cleanup-sensitive residue, or a requested annex migration.
That surface should not make `show hidden files` the main operator tool for understanding share state.

A minimal page should show:

- share and mount summary
- live-root path and current layout class
- annex location and managed byte classes
- current history/temp/metadata-carry posture
- cleanup safety summary and preservation blockers
- recent layout receipts and any pending migration steps

Primary actions should be:

- inspect layout only
- prepare annex migration
- prepare reviewed cleanup of one residue class
- preserve legacy evidence and keep inspect-only
- inspect recent layout receipts

## Relationship to other specs

This spec deliberately does **not** redefine:

- host-local path ownership (`81-target-custody-and-exclusive-bind-review-spec.md`)
- live projection and placeholder rules (`46-namespace-projection-and-placeholder-spec.md`)
- storage budgeting (`51-space-pressure-reclaim-and-retention-budget-spec.md`)
- rollback provenance (`48-history-conflict-and-rollback-provenance-spec.md`)
- metadata fidelity itself (`49-filesystem-portability-and-semantic-fidelity-spec.md`)

Instead, it forces one missing public answer:

> even when those other contracts are working, where do the sync system's own bytes live, which of them may appear in ordinary paths, and what exactly is the operator cleaning or preserving when those bytes need to move or disappear?
