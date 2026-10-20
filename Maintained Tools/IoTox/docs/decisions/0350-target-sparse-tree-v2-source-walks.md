# ADR 0350: Target sparse tree-v2 source walks

Status: accepted. Implemented 2026-09-09.

## Context

Tree-v2 sparse custody lets a node select exact include/exclude prefixes while keeping the peer from
choosing local paths. After ADRs 0344--0348 removed repeated digest and path work, a positive include
still paid avoidable source-walk cost: selected ancestor directories were walked like ordinary
selected subtrees, so a rule such as `include=shared/selected` still enumerated unrelated siblings
under `shared/`.

That was safe but wasteful. It kept sparse source publication closer to complete-tree behavior than
the custody contract requires.

## Decision

Replace the `scan_tree_v2_worktree()` recursive-directory iterator with one manual walker and add a
positive-include traversal mode.

For complete-interest namespaces, where `includes` is empty, the scanner still starts at every
source-root child and applies the same selected/unselected/conflict-root checks as before.

For positive sparse interest, the scanner now:

- reduces sorted include rules to minimal non-overlapping roots;
- observes existing ancestor directories as selected manifest entries without descending unrelated
  sibling branches;
- recursively scans only each included root/subtree, still honoring excludes and owner-control rules;
- treats an absent include root as no observed local value, leaving the existing baseline comparison
  to create tombstones only for selected paths that were previously present; and
- records `inspected_entries` and reports it as `source-inspected=` from `sync-publish` so tests and
  operators can inspect the traversal shape without relying on timings.

No branch record, manifest encoding, object identity, projection marker, wire frame, authority
capability, or peer-selected-path behavior changes.

## Consequences

Sparse local publication and bidirectional reconciliation are now closer to the selected tree size
instead of the size of every sibling below an included ancestor. This directly attacks one remaining
source-side scale bottleneck without changing merge semantics.

Paths outside positive sparse interest are outside local custody during source scanning. IoTox still
preserves unselected existing projection files during directory exchange, still refuses unsafe
selected paths and selected ancestors, and still keeps periodic full-interest behavior unchanged.

This does not remove complete projection rebuilds, unselected-preservation walks, tree-v2 range or
bundle-transfer work, auxiliary route scheduling, or intermediate-head churn. ADR 0353 later
remeasures cap 4/8/16 and makes cap 8 the current constrained-VM sweet spot, but that result does
not change this sparse source-walk boundary.

## Evidence

Owned regression coverage now includes `tree-v2 sparse scan walks only selected roots`: a worktree
with `shared/selected`, `shared/ignored`, and `private` under `include=shared/selected` inspects only
the three required entries (`shared`, `shared/selected`, and the selected file), while producing the
same two directory entries and one file entry expected by the manifest.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 && ctest --test-dir build -R "sync-tree-process" --output-on-failure'
```
