# Subject-scope contract sheet page — visibility, indexing, counting, replication, and namespace role

## Purpose

Give the operator one first surface for any serious `why is this pathname not syncing?`, `why is share size different here?`, or `can I delete this odd hidden thing?` dispute.
The page must stop the product from collapsing UI visibility, membership in sync scope, count participation, namespace role, and replication status into one vague `ignored` or `hidden` badge.

## The page must answer

1. Is this pathname a user subject, an excluded subject, a service artifact, a temporary artifact, a metadata-sidecar artifact, or an invalid-name-blocked subject?
2. Is it hidden only in the UI, or absent from indexing entirely?
3. Does it participate in share counts and size on this peer?
4. Is the exclusion local to this peer or shared by policy across peers?
5. What stronger sentence is blocked?

## Core model

### A. Namespace-role class

Represent exactly one current class:

- **Ordinary user subject**
- **Peer-excluded user subject**
- **UI-hidden but otherwise ordinary subject**
- **Service-critical artifact**
- **Temporary transfer artifact**
- **Metadata-sidecar artifact**
- **Invalid-name-blocked subject**
- **Role unresolved / manual review needed**

### B. Visibility class

Represent exactly one current class:

- **Visible in product UI**
- **Hidden by UI policy only**
- **Visible on disk but not shown by current product surface**
- **Not materialized locally**
- **Visibility unresolved**

### C. Scope-membership class

Represent exactly one current class:

- **Indexed and in scope**
- **Excluded by ignore rule**
- **Excluded by name/encoding/path validity ceiling**
- **Excluded because object is service-owned, not user-owned**
- **Excluded because object is temporary transfer residue**
- **Excluded because metadata lane is governed separately**
- **Scope unresolved**

### D. Count-participation class

Represent exactly one current class:

- **Counted in object totals and size**
- **Excluded from size but structurally known**
- **Excluded from size and indexing**
- **Service-only / not count-eligible**
- **Count participation unresolved**

### E. Divergence class

Represent exactly one current class:

- **Peer-local scope only**
- **Shared policy scope**
- **Role local but bytes shared**
- **Potential peer divergence not yet checked**
- **Divergence unresolved**

## Required warnings

The page must warn when:

- a pathname is hidden by UI policy but still fully in sync scope;
- a pathname is excluded on this peer by IgnoreList while peer scope may differ elsewhere;
- a later ignore change is being over-read as retroactive purge;
- a service artifact such as `.sync` is being treated like ordinary user content;
- `.!sync` residue is being mistaken for a healthy completed file;
- metadata-sidecar behavior depends on `StreamsList` rather than `IgnoreList`;
- the pathname is blocked because its name is unsupported rather than because transfer is failing.

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `not visible means not tracked`
- `ignored here means ignored everywhere`
- `ignored now means never announced`
- `hidden dotfile means safe to delete`
- `odd file in .sync means user residue`
- `not syncing means transfer-only failure`

## Required outputs

This page must emit a compact contract object preserving:

- namespace-role class
- visibility class
- scope-membership class
- count-participation class
- divergence class
- strongest safe sentence
- blocked stronger sentence

