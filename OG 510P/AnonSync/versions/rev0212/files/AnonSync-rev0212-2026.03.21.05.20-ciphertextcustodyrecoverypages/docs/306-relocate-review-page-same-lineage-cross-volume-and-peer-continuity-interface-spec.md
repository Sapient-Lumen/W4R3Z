# Relocate review page: same-lineage, cross-volume, and peer continuity interface spec

## Purpose

This page owns the reviewed answer for non-trivial local path change.

It answers:

> is this move a harmless same-lineage relocation, a cross-volume rebind, a target adoption, or a continuity-breaking detach/reconnect that needs explicit peer fallout review?

This page exists so AnonSync does not regress into `move it and see`, `Folder not found`, or disconnect/reconnect folklore.

## Core rule

Any relocation that is not clearly an in-place same-domain move must compile to one **Relocate review** page before apply.

That includes at least:

- cross-volume or cross-partition moves
- moves on constrained/sandboxed seats
- reattachment after a path disappears
- rebinding to a previously used directory
- rebinding to a non-empty target
- changes that would sever or recreate local service material

## Fixed review order

Every relocation review renders the same sections:

1. proposed change
2. continuity class
3. target condition
4. peer / authority fallout
5. preservation plan
6. actions and receipt promise

### 1) Proposed change

Show:

- current path
- proposed path
- current storage domain
- proposed storage domain
- who initiated the move
- reason / trigger

### 2) Continuity class

Choose one:

- `same-domain relocate`
- `cross-domain rebind`
- `reattach old location`
- `adopt existing tree`
- `path repair after disappearance`
- `blocked`

This verdict is the semantic center of the page.

### 3) Target condition

Show:

- empty / non-empty / previously-bound / missing / unreadable
- lineage evidence
- whether additional reconciliation review is required
- whether service material would move with the subject or be regenerated

### 4) Peer / authority fallout

Show:

- whether peer relationships remain intact
- whether any reconnect or re-share would be required
- whether other seats see a semantic rename, no visible change, or increased repair risk
- whether future arrivals/templates on this seat change or remain unchanged

### 5) Preservation plan

Show:

- bytes preserved in place
- bytes quarantined first
- receipts that will be written
- rollback / fallback rung if apply fails

### 6) Actions and receipt promise

Actions:

- `Apply same-lineage relocate`
- `Open reconciliation first`
- `Prepare path repair`
- `Keep current bind`
- `Convert to pathless presence`

Receipts must prove:

- old path
- new path
- continuity class
- target condition
- peer fallout verdict
- whether any reconnect / re-share / reindex / quarantine was required

## Page rules

### Rule 1 — cross-volume is not just a path edit

A cross-domain move must publish stronger continuity consequences than an in-place rename.

### Rule 2 — missing-path repair and deliberate relocation share one grammar

The operator should not have to learn two different products for `the path vanished` and `I want to move this safely`.

### Rule 3 — peer fallout must be first-class

If the safest path is `remove and re-add`, the page must say what prior relationships that would sever.
That truth cannot be hidden behind a later troubleshooting article.

## Honest outputs

The page may conclude:

- `apply safely now`
- `needs reconciliation first`
- `requires peer-continuity reset`
- `blocked here`
- `convert to pathless presence instead`

It may not collapse those into one `change location` control.
