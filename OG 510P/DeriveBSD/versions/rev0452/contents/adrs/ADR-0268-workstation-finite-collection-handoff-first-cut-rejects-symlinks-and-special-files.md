# ADR-0268: Workstation finite collection handoff first cut rejects symlinks and special files

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` fixed the first retrieve-width cut: single-retrieve by default and auto-stopping after the first successful retrieve.
`ADR-0265` fixed selected directories as snapshot-shaped membership instead of live tree authority.
`ADR-0266` fixed that reviewed snapshot membership stays manifest-first.
`ADR-0267` fixed that the first richer lane stays read-only only.

That still left one high-leverage ambiguity inside `RFC-0194`:
**what member kinds are actually allowed inside the first manifest-first collection handoff?**

Without a hard answer here, “selected folder snapshot” can quietly smuggle live namespace resolution or active host endpoints back into the first richer lane:
- following symlinks can reach beyond the reviewed tree,
- preserving symlink objects pushes later path resolution back onto the receiver,
- and special filesystem objects such as device nodes, FIFOs, or sockets are active authority surfaces rather than boring file handoff members.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the first cut allows only **regular-file manifest entries** and **explicit directory manifest entries**.
2. selected directories still expand into explicit reviewed descendant-member entries at handoff creation time.
3. **symlinks are not part of the first cut**; the lane does not silently follow, preserve, or reinterpret them.
4. **special filesystem objects are not part of the first cut**, including device nodes, FIFOs, sockets, and equivalent active or host-coupled objects.
5. if a reviewed selection contains unsupported member kinds, handoff creation must **fail closed** or require explicit pre-normalization outside this lane; the broker must not silently omit, dereference, or coerce them.
6. any later attempt to standardize symlink preservation, symlink-following snapshot rules, special-object handoff, or provider/virtual-object variants must return as an explicit follow-on RFC/ADR decision.

## Consequences

- The first richer lane stays a boring reviewed collection handoff instead of an accidental path-resolution or ambient-endpoint lane.
- Manifest-first review/export remains portable: the trusted UI can explain what is present without a hidden “and also whatever that symlink resolved to later” clause.
- Empty directories can still be preserved through explicit directory entries, while active/special objects stay out of scope until proven worth the support and laundering cost.

## Alternatives considered

- **Follow symlinks at handoff creation time:** rejected because it quietly widens reviewed membership through path resolution and makes the reviewed set depend on snapshot-time namespace behavior.
- **Preserve symlink objects as first-class members in the first cut:** rejected because later receiver-side resolution turns a reviewed collection lane back into ambient namespace semantics.
- **Silently omit unsupported members:** rejected because the reviewed user selection and the actual handed-off set would diverge without clear evidence.
- **Support “all filesystem object kinds” from day one:** rejected because the first richer lane is supposed to stay smaller than a general document-provider or filesystem-virtualization subsystem.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
