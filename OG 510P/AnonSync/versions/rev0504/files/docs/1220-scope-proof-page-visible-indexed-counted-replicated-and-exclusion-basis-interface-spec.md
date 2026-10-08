# Scope proof page — visible, indexed, counted, replicated, and exclusion basis

## Purpose

After any serious `why is this missing?` or `was this ever really in scope here?` dispute, a later operator must be able to answer without reopening IgnoreList folklore or `.sync` archaeology.
This page exists because visibility, indexing, counting, replication, and namespace role weaken differently.

## Proof ladder

### Rung 1 — pathname known only

We know the pathname exists in some namespace or report.
We do **not** yet know whether it is ordinary user content, in sync scope, counted, or replicated.

Show:

- pathname identity
- current namespace-role hypothesis
- current visibility class
- no indexing proof yet

Allowed sentence:

- `pathname known, scope still weak`

Blocked stronger sentence:

- `this was syncing here`

### Rung 2 — visible but scope-uncertain

We know the pathname is visible on disk or in UI.
We do **not** yet know whether it is excluded, service-owned, or merely hidden.

Show:

- visibility basis
- possible namespace roles still in play
- whether the object is under `.sync`
- whether hidden-file UI policy may be involved

Allowed sentence:

- `pathname visible, scope membership not yet proven`

Blocked stronger sentence:

- `visible means counted and replicated`

### Rung 3 — exclusion basis proven

We know why the pathname is out of scope on this peer.

Show:

- ignore, service-owned, metadata-lane, temp-transfer, or invalid-name basis
- whether the exclusion is peer-local or shared policy
- whether structural announcement may predate the exclusion
- whether size/count omission is expected

Allowed sentence:

- `exclusion basis proven for this peer`

Blocked stronger sentence:

- `this pathname was never known anywhere`

### Rung 4 — in-scope and count-participating

We know the pathname is indexed and participates in counts/size on this peer.
We may still not know full replication outcome elsewhere.

Show:

- indexing proof
- count participation proof
- namespace role still ordinary
- remaining peer-divergence uncertainty if any

Allowed sentence:

- `in scope and count-participating on this peer`

Blocked stronger sentence:

- `replicated successfully to every peer`

### Rung 5 — replicated or divergence explained

We know either that replication occurred as expected or that peer divergence fully explains why another peer disagrees.

Show:

- replication witness or divergence explanation
- whether peer-local ignore rules are the cause
- whether later rule timing weakens stronger claims
- whether any service/temp artifacts muddied prior observations

Allowed sentence:

- `scope result explained at peer level`

Blocked stronger sentence:

- `all peers shared one identical scope contract`

## Required side proofs

The page must also show:

- whether hidden-file UI policy affected the observation
- whether `.sync` ownership changed how the pathname should be treated
- whether xattr transport used a sidecar lane outside IgnoreList authority
- whether temp-residue deletion would destroy evidence needed for recovery
- whether unsupported-name remediation is required before the pathname can become ordinary user scope

## Compact output

The page must produce:

- `scope_confidence` (`known_only`, `visible_uncertain`, `excluded_proven`, `in_scope_counted`, `replicated_or_divergence_explained`)
- `namespace_role`
- `peer_scope_divergence`
- `count_participation`
- `blocked_stronger_sentence`

