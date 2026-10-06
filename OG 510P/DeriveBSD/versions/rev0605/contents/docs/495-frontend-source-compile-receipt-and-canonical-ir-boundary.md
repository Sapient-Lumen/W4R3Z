# Frontend source / compile receipt / canonical IR boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability  
**Patterns:** Adapter→Shadow→Replace, Plan→Apply→Receipt  

DeriveBSD already wanted “frontend → canonical IR”, but one expensive question was still fuzzy:

> when humans or tools author CUE / Pkl / HuJSON / Starlark, which object actually has authority, and where does compiler evidence live?

This doc fixes that boundary for v0.

## Accepted boundary

The authoritative object is the compiled canonical JSON artifact:

- `system.spec`
- `minimal.spec`
- `microvm.spec`
- `trust-policy`
- other schema-versioned canonical JSON policy/spec objects

The evidence-only object is:

- `frontend.compile.receipt`

That means:

- frontend source text is authoring context, not authority
- compiler traces and diagnostics are support/review evidence, not policy
- the Derive core still keys on canonical JSON digests
- richer frontends do not get to silently redefine semantics after review

## `frontend.compile.receipt` is evidence-only

`spec/frontend.compile.receipt.schema.json` carries `authority_semantics = frontend-compilation-evidence-only`.

The receipt records the minimum useful facts about a frontend compilation step:

- which frontend kind was used
- which source digests participated
- which compiler/tool artifact digest ran
- which invocation profile / IO posture was allowed
- which compiled authoritative object digest came out
- optional trace / diagnostics digests for explainability

This gives DeriveBSD one place to preserve authoring provenance without making the frontend runtime part of the core evaluator.

## v0 blessed in-tree authoring surfaces are intentionally minimal

DeriveBSD now makes one conservative product decision:

- canonical JSON is blessed in-tree
- HuJSON/JWCC-style human JSON normalization is blessed in-tree
- richer frontends remain adapter lanes

That means a user can get ergonomic comments/trailing commas for human-edited policy without forcing the archive to choose a full frontend language stack up front.

## CUE / Pkl / Nickel / Starlark remain adapter lanes

These frontends may still be valuable.
They can validate, reduce boilerplate, and emit useful “why is this value here?” traces.

But in v0 they stay outside the core product contract:

- they compile to canonical JSON
- they may emit `frontend.compile.receipt`
- they do not become authoritative on their own
- they must stay killable under Adapter→Shadow→Replace discipline

This is the key anti-sprawl move.
DeriveBSD refuses to let “which frontend somebody happened to use” become the hidden semantics of the system.

## Conservative IO posture is part of the boundary

Official docs for modern config languages show real compiler conveniences such as JSON export, module systems, file embedding, and external readers. Those are useful, but they are also exactly how a frontend stops being “just authoring ergonomics” and turns into a second evaluator.

So the v0 default posture is explicit:

- JSON/HuJSON need no ambient imports or network
- richer frontends must treat imports, file embedding, and external readers as explicit bounded inputs
- A and D should stay especially conservative by default, because supply-chain and audit costs dominate any ergonomic win

## Product-shape fit (A–D without forks)

- **A / fleet host:** JSON/HuJSON remains sufficient for the base path; richer frontends can exist for internal tooling but do not become hidden authority.
- **B / workstation:** local ergonomics can improve through adapter frontends while the reviewed object remains canonical JSON and exportable evidence remains stable.
- **C / general-purpose OS:** richer frontends stay viable for power users, but they do not force the core product to inherit a large DSL TCB.
- **D / appliance factory / regulatory:** receipts for the authoring/compiler step help explain provenance, while the authoritative object stays small, portable, and long-lived.

## Why this is the right small hard decision

Choosing a “best frontend language” now would widen scope and lock DeriveBSD to a fast-moving toolchain question.

Choosing a crisp authority boundary now is cheaper and more useful:

- one canonical authoritative object
- one standard evidence object for source/compiler provenance
- one conservative v0 blessing (JSON + HuJSON)
- richer languages still possible, but not allowed to become folklore authority

## Related docs

- `adrs/ADR-0085-frontend-source-compile-receipt-and-canonical-ir-boundary.md`
- `docs/79-derive-spec-frontends.md`
- `docs/83-evaluator-minimalism.md`
- `docs/149-human-policy-hujson-and-canonicalization.md`
- `docs/229-evidence-spine-overview.md`
- `spec/frontend.compile.receipt.schema.json`
- `spec/examples/frontend.compile.receipt.json`
- `spec/examples/trust.policy.hujson`
- `spec/examples/trust.policy.json`

Last updated: 2026-03-23r430
