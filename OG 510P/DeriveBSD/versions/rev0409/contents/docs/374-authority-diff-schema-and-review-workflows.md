# Authority diffs as a first-class artifact (schema + review workflow)

`authority.diff` is the “boring diff” that answers:
- what new authority exists between generations?
- who gained it?
- what is the review surface?

This doc makes `authority.diff` **machine-checkable**, aligning it with other surface-diff artifacts like `contract.diff` and `uapi.diff`.

See:
- authority graph substrate: `docs/366-capability-graphs-and-authority-diff-surfaces.md`
- blast-radius diffs: `docs/106-blast-radius-diff.md`
- contract diffs: `docs/370-contract-registries-and-api-diff-gates.md`
- kernel UAPI diffs: `docs/362-uapi-surface-registry-and-compat-gates.md`

## The object

- Schema: `spec/authority.diff.schema.json`
- Example: `spec/examples/authority.diff.json`

`authority.diff` is intentionally *summary-first*:
- it is not trying to encode every detail of two full graphs
- it captures the **delta** plus **risk classification hooks**

## Review workflow (how it’s used)

1) CI derives `capability.graph` for each generation (see `spec/capability.graph.schema.json`).
2) CI computes `authority.diff` between two generations.
3) Policy evaluates the diff:
   - allow, block, or require explicit override receipts
4) Human reviewers get a short summary:
   - new “danger edges”
   - new parsers/endpoints
   - new persistence reach

## What counts as “new authority”

Treat these as the highest-signal buckets (review should focus here):

- **New parsers** (accept untrusted input): new RPC/portal endpoints, new ioctls, new device protocols. Where possible, link these to `parser.registry` / `parser.diff` for machine-checkable parser surface drift (see `docs/376-parser-surface-registry-and-fuzz-gates.md`).
- **New ambient reach**: broad filesystem reach, broad network egress, host-admin hooks.
- **New persistence authority**: new write access to datasets, new backup/export rights.
- **New identity edges**: new signing keys, new workload identities, new operator session scopes.

These buckets deliberately align with:
- contract diffs (`contract.diff`)
- UAPI diffs (`uapi.diff`)
- evidence receipts (who granted/used it)

## Design constraints

- **Stable IDs**: nodes and edges referenced in diffs must have stable identifiers.
- **Digest-first**: new authority should be keyable on `cap.kind` + `cap.digest`.
- **Explainability**: a diff entry should carry a short rationale, and ideally an RFC/ADR pointer.

## Promotion gates

A practical default gate for stable channels:
- forbid any new `risk_tags` unless:
  - the change includes a matching contract/UAPI diff classification, and
  - the reviewer attaches an explicit “approved authority delta” receipt

This keeps “permission creep” from becoming the steady-state.
