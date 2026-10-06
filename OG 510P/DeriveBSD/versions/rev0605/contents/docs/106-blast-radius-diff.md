# Blast-radius diffs (authority deltas)

DeriveBSD diffs should not only answer “what changed”, but also:

> “What new authority does the new thing have?”

## Examples of blast-radius surfaces

- filesystem: new writable paths, new mount permissions
- network: new egress/ingress allowances (pf anchors)
- devices: new devfs nodes exposed
- runtime: new privileges/capabilities, new syscalls policy
- compat: new libmap/hints mappings

**Cross-cutting drift surfaces (review gates):**
- contracts: new RPC/portal endpoints (contract digests)
- kernel UAPI: new/changed ioctl/sysctl/devnode surfaces
- parsers: new or broadened parsers/decoders (untrusted bytes → structured objects)
- resources: new budgets/quotas/default limits
- trust boundaries: new or widened crossings (control changes / untrusted-input edges)
- crypto: new protocols/suites/key policies (crypto drift as a review surface)

## CLI shape (design)

- `derive diff --blast-radius plan A B --json`
- `derive diff --blast-radius deployment old new --json`

## Output (structured)

The diff is a stable JSON object so tooling (and policy gates) can reason about it.

Blast-radius diffs are derivable from more specific artifacts:
- `authority.graph` / `authority.diff` (authority edges)
- `contract.registry` / `contract.diff` (interfaces)
- `uapi.registry` / `uapi.diff` (kernel surfaces)
- `parser.registry` / `parser.diff` (decode surfaces)
- `trust.boundary.graph` / `trust.boundary.diff` (threat boundary drift)
- `crypto.registry` / `crypto.diff` (crypto surfaces)

Blast-radius diffs focus on authority deltas. For “what new code exists now?”, use `closure.diff`.
Drift bundles (`drift.bundle`) are the preferred review attachment: they link `blast_radius.diff` alongside the underlying diffs and evidence.
See: `docs/396-closure-diffs-and-new-code-surfaces.md`, `docs/395-drift-bundles-and-review-summaries.md`.

## Wiring

See:
- schema: `spec/blast_radius.diff.schema.json`
- example: `spec/examples/blast_radius.diff.json`

Related:
- authority diffs: `docs/366-capability-graphs-and-authority-diff-surfaces.md`, `docs/374-authority-diff-schema-and-review-workflows.md`
- contract diff gates: `docs/370-contract-registries-and-api-diff-gates.md`
- UAPI diff gates: `docs/362-uapi-surface-registry-and-compat-gates.md`
- parser diff gates: `docs/376-parser-surface-registry-and-fuzz-gates.md`
- trust boundary diffs: `docs/380-trust-boundary-graphs-and-threat-diff.md`

See RFC-0075.
Last updated: 2026-02-27r108
