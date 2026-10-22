# RFC-0001: ViewFS foundation slice

## Status
Draft

## Problem
SlopOS needs a filesystem story, but building “a custom filesystem” is too vague. If we over-specify too early, we risk freezing the wrong abstractions. If we under-specify, compatibility pressure will quietly recreate ambient host filesystem authority.

## Proposal
For the first serious design slice, ViewFS should commit to:
1. immutable-first object storage,
2. object handles with explicit rights,
3. explicit per-process view roots,
4. portal-mediated imports/exports,
5. path compatibility as a subordinate membrane.

## Deliberate non-decisions
This RFC does **not** settle:
- final on-disk pack format,
- hash algorithm,
- rich mutable transaction model,
- revocation mechanics,
- distributed sync/replication,
- query/index architecture,
- final shell language syntax,
- grouped capability bundle semantics.

## Rationale
- REF-VENTI, REF-GIT-OBJECTS, and REF-NIX-CA argue for a boring immutable core.
- REF-EROS and REF-KEYKOS warn that durable authority graphs are not a “later detail.”
- REF-FUCHSIA-NAMESPACE and REF-WASMTIME-PREOPEN suggest a clean separation between explicit roots and compatibility paths.
- REF-XDG-FILECHOOSER and REF-XDG-DOCUMENTS suggest that import/export should be mediated and receipt-bearing.
- REF-IPFS-MFS and REF-SQLITE-SESSION suggest a useful place to look if mutable work-state ergonomics are needed before a full mutable store exists.

## Sketch
### Object kinds
- Blob
- Directory
- Manifest
- View
- GrantReceipt

### Tentative APIs
- `view.create()`
- `view.bind(slot, handle, rights)`
- `view.resolve(path-within-view)`
- `obj.inspect(handle)`
- `portal.open()`
- `portal.save()`

## Risks
- compatibility pressure could quietly become the primary model
- snapshot roots could be mistaken for a full mutable filesystem story
- portal semantics could be hand-waved before revocation/persistence are clear
- grouped capability bundles could sneak in as an unreviewed convenience layer

## Evidence plan
- prototype a minimal object store + handle table
- prototype a preopen-style compat membrane
- prototype a chooser/import receipt flow
- pressure-test shell UX with block transcripts and clickable receipts
- only then explore mutable work-state sidecars, bundle semantics, or richer query layers
