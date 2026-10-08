# Namespace projection and placeholder spec

## Purpose

The archive already had ignore rules, projection policies, and a few flows showing why namespace and local view should not be conflated.
What it still lacked was a sharper product answer to another deceptively simple operator question:

> when I hide a path, who exactly stops seeing its name, who still keeps local bytes, and what changes if I tighten that rule after the tree was already indexed or materialized?

Resilio's current docs are useful here precisely because they show why this cannot stay fuzzy.
They say `IgnoreList` lives in hidden `.sync`, does not affect files that already synced, and still leaves already-indexed structure stored in the database and passed to peers until disconnect. Separate docs say placeholders / `.rsls` represent names without bytes, deleting a local file in Selective Sync can revert it to a placeholder, disconnecting a selective-sync share removes placeholders from the device, xattrs bypass `IgnoreList` and require `StreamsList`, and nested subfolder shares disable Selective Sync while creating extra indexing work.
Those are understandable implementation choices, but they are not one coherent operator model.

This document turns that lesson into an AnonSync requirement:

- share namespace visibility
- peer announcement posture
- mount-level omission / placeholder / metadata-only / full view
- local byte presence or eviction
- already-indexed / already-materialized tightening effects

must be inspectable through one shared projection grammar.

## Core stance

1. **Ignore is not the whole story.**  
   Ignoring a path, suppressing its share namespace, omitting it locally, and evicting bytes are separate actions.

2. **Hidden service files are never the operator contract.**  
   `.sync`, `IgnoreList`, `StreamsList`, or future implementation caches may exist internally, but the supported product model must not require remembering their quirks.

3. **Late tightening must say what changed.**  
   When a rule becomes stricter after indexing or materialization already happened, the product must issue an explicit effect report and, after apply, a durable receipt.

4. **Local view changes are not share-namespace changes.**  
   A laptop may omit or placeholder a path locally without implying peers stopped learning the name.

5. **Byte eviction is not namespace erasure.**  
   A file becoming placeholder-visible or locally absent does not itself mean the share stopped announcing it.

6. **Projection is not a backdoor filesystem-compatibility control.**  
   Metadata-stream posture, xattr fidelity, and special-file safety still belong to filesystem compatibility and related specs.

## Projection axes

The interface should expose at least these distinct axes for any concrete path:

- `share-namespace` (`visible`, `hidden`)
- `peer-announcement` (`announce`, `suppress-new`, `retract-reviewed`)
- `local-view` (`omit`, `placeholder`, `metadata-only`, `full`)
- `local-bytes` (`absent`, `materialized`, `preserved-only`, `eviction-pending`)
- `history-of-visibility` (`never-indexed`, `indexed-local`, `announced-remote`, `materialized-local`, `mixed-history`)

These are not implementation threads.
They are operator-meaningful slices of projection truth.

A path may therefore truthfully be in a state like:

- hidden from future peer announcement
- still review-required because remote peers already learned the directory shape
- omitted on this mount
- local bytes preserved elsewhere pending safe eviction

That is a much better answer than the single word `ignored`.

## Effective projection state

### Projection policy

This object already exists in the archive.
This document sharpens what it must mean.

Fields:

- `projection_policy_id`
- `scope_type` (`share`, `mount`)
- `scope_id`
- `default_share_namespace` nullable (`visible`, `hidden`)
- `default_peer_announcement` nullable (`announce`, `suppress-new`, `retract-reviewed`)
- `default_local_view` nullable (`omit`, `placeholder`, `metadata-only`, `full`)
- `tighten_behavior` (`review-existing`, `leave-visible`, `safe-evict-local`, `block-until-settled`)
- `ordered_rules[]`
- `effective_health` (`ok`, `review-required`, `receipt-pending`, `blocked`)
- `provenance_ref` nullable
- `updated_at`

Rules:

- share-scoped policies control namespace visibility and what new peers are told
- mount-scoped policies control what one local binding shows or materializes
- a mount-scoped policy may not silently widen share namespace
- `tighten_behavior` is part of the public contract, not a hidden implementation choice

### Projection effect report

A first-class report answering what a proposed or newly effective projection change means for one concrete path or prefix.
It should always say:

- before/after share namespace truth
- before/after peer announcement posture
- before/after local view on relevant mounts
- existing indexed/materialized history
- whether follow-up is `none`, `review`, `safe-evict`, `settlement-barrier`, or `blocked`
- whether a receipt will be emitted if applied

This report should be used for both preview and post-change explanation.
It keeps projection changes from collapsing back into folklore.

### Projection receipt

A durable record that a high-signal projection change was applied and what it actually touched.

Fields:

- `projection_receipt_id`
- `change_class` (`namespace-tighten`, `namespace-widen`, `local-tighten`, `local-widen`, `detach-cleanup`, `materialization-default-change`)
- `scope_type` (`share`, `mount`)
- `scope_id`
- `selector_summary`
- `before_effective_state`
- `after_effective_state`
- `prior_history_of_visibility`
- `followup_required` (`none`, `review`, `safe-evict`, `settlement-barrier`, `blocked`)
- `followup_refs[]`
- `applied_by`
- `applied_at`
- `provenance_ref` nullable

Receipts matter because later audit should not have to infer whether a change:

- merely hid clutter locally
- stopped announcing names to peers
- requested retraction review for already-announced structure
- evicted bytes locally
- just removed placeholders during detach

## Transition rules

### 1) Tightening before indexing or materialization

If a path was never indexed and never materialized locally, tightening may be direct.
The resulting receipt can still be simple.
No drama is needed where no real visibility history exists.

### 2) Tightening after indexing already happened

If peers may already know the path name or directory shape, the product must not pretend a policy edit rewrote history.
Instead it should:

- produce a projection effect report
- say whether the rule changes only future announcement or also requests reviewed retraction
- say whether settlement or peer review is needed before claiming the tighter state is complete
- emit a projection receipt after apply

This avoids the false promise that “hidden now” means “nobody ever saw it.”

### 3) Tightening local view after bytes already exist

If a mount changes from `full` or `placeholder` toward `omit`, the product must say what happens to local bytes:

- leave in place
- preserve elsewhere then omit
- safe-evict and keep a receipt
- block because preservation is too weak

A local omit change must never silently imply share deletion.

### 4) Widening visibility

A widening change is simpler than tightening, but it still needs an honest before/after record.
The product should not silently reopen a namespace path or rematerialize bytes without a receipt on high-signal changes.

### 5) Detach and disconnect

Detaching a mount or disconnecting a share may change local view drastically.
That still does not equal share-namespace suppression.
If placeholders disappear from the filesystem because a mount is detached, the resulting receipt must classify that as local cleanup, not peer-facing retraction.

### 6) Nested or topology-trick workarounds are not the supported model

The product should not require operators to create nested shares, local loopback shares, or topology tricks just to get different namespace exposure or local projection.
Those may remain advanced internals or future features, but the supported answer should be projection policy, not double indexing folklore.

## Relationship to ignore rules

Ignore rules remain useful.
They are still distinct from projection policy.

A good mental model is:

- ignore rules answer what should not be tracked as part of ordinary share input
- share projection answers what peer namespace should be visible or suppressed
- mount projection answers what one local binding should show
- materialization answers whether bytes are present here

The CLI and workbench should present those as neighboring tools, not as one overloaded checkbox.

## CLI surface

The archive already has `anonsync projection show`, `test`, and `add`.
This document adds a clearer preview and receipt surface around them.

### Read effective projection truth

```text
anonsync projection show --share codebase
anonsync projection show --mount mnt_01J...
anonsync projection test codebase build/output/app.tar
anonsync projection explain --share codebase --path build/output/app.tar
```

Output should say at least:

- share namespace visibility
- peer announcement posture
- local view per relevant mount
- local byte posture on this device
- history of visibility if known
- whether a late-tightening review is required

### Prepare tighter rules

```text
anonsync projection add codebase --match 'build/**' --namespace hidden --announce suppress-new
anonsync projection add mnt_01J... --match 'build/**' --local omit
anonsync projection prepare-tighten codebase --path build/output/app.tar --plan
```

`prepare-tighten` should produce or reference a projection effect report whenever the change is not trivially fresh.

### Inspect receipts

```text
anonsync projection receipt list --share codebase
anonsync projection receipt show prc_01J...
```

Receipts should render clearly enough that later audit can answer whether a change was peer-facing, local-only, or both.

## API expectations

The daemon API should expose at least:

```text
GET    /v1/projection-policies
POST   /v1/projection-policies
GET    /v1/projection-policies/{projection_policy_id}
PATCH  /v1/projection-policies/{projection_policy_id}
DELETE /v1/projection-policies/{projection_policy_id}
POST   /v1/projection-policies/{projection_policy_id}/test
POST   /v1/projection-policies/{projection_policy_id}/prepare-tighten
GET    /v1/projection-receipts
GET    /v1/projection-receipts/{projection_receipt_id}
```

`POST .../prepare-tighten` should be allowed to return either a directly applicable low-risk response or a `projection-effect` report that requires review.

## Workbench expectations

The workbench should gain one stable card or tab: **Namespace & local view**.

That surface should show:

- share namespace defaults
- peer announcement posture
- mount-by-mount local view posture
- a path-test panel with before/after projection truth
- review-required previously indexed or materialized paths
- recent projection receipts

The home surface should also be able to surface:

- a projection tighten waiting for review
- a recent local-only cleanup so it is not mistaken for share deletion
- a suppression rule whose peer-facing retraction is still unsettled

## Safety thresholds

1. A policy edit must never silently claim past remote visibility was erased.
2. Any change that affects peer namespace after indexing should normally create a projection effect report.
3. Local omit / placeholder changes must display local byte consequences explicitly.
4. Detach cleanup must not masquerade as share-wide suppression.
5. Projection receipts should be durable enough for later audit and cutover review.

## Why this matters

Resilio's current docs are honest enough to teach the lesson clearly:

- ignore behavior lives in hidden `.sync` files
- late ignore edits still leave already-indexed structure visible to peers until disconnect
- placeholders are a local projection mechanism, not the whole namespace model
- xattrs use a separate hidden control file family
- nested subfolder sharing uses topology and extra indexing rather than one public projection grammar

AnonSync should learn from the utility while refusing the hidden-coupling model.
The operator should be able to answer “who sees the name, who has the bytes, and what changed when I tightened this?” without reading support lore.
