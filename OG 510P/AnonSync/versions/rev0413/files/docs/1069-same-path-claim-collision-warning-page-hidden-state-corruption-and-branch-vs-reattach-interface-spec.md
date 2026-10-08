# Same-path claim collision warning page, hidden-state corruption, and branch-vs-reattach interface spec

## Purpose

One of the most dangerous local mistakes is not `running a second process`.
It is **letting two local runtimes claim the same continuity-bearing subject path**.

Current official Resilio docs still say that if a folder is added to Sync A and then to Sync B on the same computer, or if one external disk is reused as storage for two instances, the former instance's internal files can be corrupted and synchronization can become impossible.
AnonSync should surface that truth before mutation, not as repair folklore after damage.

## When this page appears

Show this page whenever a proposed local bind intersects any of the following:

- an existing AnonSync service-state marker under the target path
- a path already claimed by another live or dormant local runtime
- removable/external media with unresolved runtime lineage
- a proposed `add existing folder` or `attach target` that would reuse the same continuity-bearing path across namespaces

## Fixed review order

1. **Collision claim**
2. **Continuity-bearing material at risk**
3. **Safe alternatives**
4. **Blocked stronger sentences**
5. **Decision receipt preview**

### 1) Collision claim

Show:

- incumbent runtime namespace
- requested runtime namespace
- exact overlapping path
- overlap class (`same-root`, `ancestor/descendant`, `shared-storage-root`, `external-media-reuse`, `unknown`)
- proof strength (`marker-proven`, `receipt-proven`, `path-only`, `ambiguous`)

### 2) Continuity-bearing material at risk

Show what would be endangered if double-claim were allowed:

- local service-state markers
- path identity / subject binding material
- archive/history association
- lineage receipts that would become ambiguous
- future repair burden if corruption occurs

Do not reduce this to `folder already in use`.

### 3) Safe alternatives

Offer only typed alternatives such as:

- `open incumbent runtime`
- `reattach to incumbent world`
- `migrate subject ownership`
- `create reviewed branch on a different target path`
- `inspect without binding`
- `detach incumbent claim first`

Each alternative must say whether continuity is preserved, split, or abandoned.

### 4) Blocked stronger sentences

Always show the stronger blocked claims, for example:

- `running both is safe because they are separate processes`
- `same disk path is safe because storage roots differ`
- `external drive reuse is harmless if I only need a quick test`

### 5) Decision receipt preview

Preview the exact future receipt classes:

- `claim blocked pending migrate review`
- `claim redirected into safe branch review`
- `incumbent claim detached and successor accepted`
- `collision evidence ambiguous; inspect-only opened`

## Public objects

### `same_path_claim_collision_warning`

Fields:

- `same_path_claim_collision_warning_id`
- `incumbent_namespace_ref`
- `requested_namespace_ref`
- `overlap_path_ref`
- `overlap_class`
- `proof_strength`
- `risked_material_classes[]`
- `safe_alternatives[]`
- `blocked_stronger_sentences[]`
- `reviewed_at`

## Allowed actions

Allowed primary actions:

- `Open incumbent`
- `Prepare migrate review`
- `Prepare safe branch review`
- `Open inspect-only`
- `Cancel requested bind`

Disallowed primary actions:

- `Bind anyway`
- `Take over silently`
- `Overwrite incumbent marker`

## Design tests

The page fails if any of these remain true:

- the product still teaches same-path double claim mainly through later corruption symptoms
- `already syncing` warnings can appear without saying what continuity-bearing material is at risk
- branch creation and reattach still read like the same decision
- removable-media reuse still looks safer than it is just because the original runtime is offline

## Non-clone reason

Current official Resilio docs still reserve the clearest same-path collision sentence for a repair article.
AnonSync should move that sentence earlier into a dedicated warning-and-alternatives page.
