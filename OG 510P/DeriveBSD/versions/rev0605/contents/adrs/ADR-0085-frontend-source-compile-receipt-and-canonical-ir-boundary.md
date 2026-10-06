# ADR-0085: Frontend source / compile receipt / canonical IR boundary

- Status: Accepted
- Date: 2026-03-07

## Context

DeriveBSD already had the right instinct in ADR-0023 and `docs/79-derive-spec-frontends.md`:

- the authoritative Spec / policy object is canonical, schema-versioned JSON
- authoring frontends are compiler lanes rather than part of the Derive core
- the evaluator must stay code-free

But one expensive ambiguity remained:

1. Is a frontend source file itself authoritative, or only authoring context?
2. Where do source digests, compiler digests, invocation profile, and “why did this field end up here?” traces live without letting the frontend become the product?
3. Which frontends are actually blessed in-tree for v0, and which remain adapter lanes?

If left vague, richer frontend tooling would silently become a fast-moving second policy/evaluation plane.

## Decision

1. The authoritative object remains the compiled canonical JSON artifact (`*.spec`, `trust-policy`, etc.).
   Frontend source text is never the source of authority.

2. `frontend.compile.receipt` is evidence only.
   It binds:
   - source frontend kind
   - source digests
   - compiler/tool artifact digest
   - invocation profile and IO posture
   - optional trace / diagnostics digests
   - the digest of the compiled authoritative JSON object

   The schema carries `authority_semantics = frontend-compilation-evidence-only`.

3. v0 blesses only the minimal in-tree authoring surfaces:
   - canonical JSON
   - HuJSON/JWCC-style human JSON normalization to canonical JSON

4. Richer authoring languages such as CUE / Pkl / Nickel / Starlark remain optional adapter lanes.
   They may compile to canonical JSON and emit `frontend.compile.receipt`, but they are not part of the Derive core contract and must not redefine authority.

5. For higher-assurance product shapes, the default posture for richer frontend lanes is conservative:
   - no ambient network access
   - no ambient external readers / resource readers
   - no silent file embedding or imports beyond explicitly bounded workspace/locked inputs

   Looser frontend capabilities remain explicit adapter territory.

## Consequences

- reviewers can reason about one authoritative object and one optional evidence object instead of arguing about whether source text or compiler behavior is the real product
- support and forensics can preserve “how this JSON was produced” without forcing the runtime or policy engine to understand the frontend language
- A/B/C/D stay viable without forks because the product-default path is still JSON/HuJSON, while richer local ergonomics remain possible as bounded adapter lanes
- future frontend work now has a narrow contract to plug into instead of inventing bespoke compiler metadata each time

## Why this is narrow enough

This does not bless a new configuration language.
It does not redesign modules, templates, or explain traces.
It only fixes the authority boundary:

- authoritative compiled JSON object
- evidence-only frontend compilation receipt
- minimal blessed in-tree authoring surfaces

That is a small, high-leverage revision with bounded implementation scope.
