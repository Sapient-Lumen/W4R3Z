# ADR-0289: Package recipe surface stays evaluator-free and restricted-pipeline-first

- Status: Accepted
- Date: 2026-03-23

## Context

The archive already made three important partial cuts:

- `docs/83-evaluator-minimalism.md` and ADR-0025 fixed that the Derive core must not execute user code during evaluation.
- `adrs/ADR-0085-frontend-source-compile-receipt-and-canonical-ir-boundary.md` fixed that richer authoring frontends compile to canonical JSON and remain evidence-backed adapter lanes.
- `rfcs/RFC-0091-declarative-image-pipelines.md` and `docs/134-declarative-image-pipelines-apko-melange.md` identified a promising **restricted recipe lane** for high-assurance builds.

But the archive still left one expensive ambiguity in `docs/266-open-questions-and-risk-register.md`:

> how much language is allowed for package/build recipes?

If left vague, DeriveBSD would likely drift toward one of two bad outcomes:

1. a general-purpose recipe language quietly becomes the real product, while typed Spec/Plan objects become veneers; or
2. every package/import/build lane smuggles its own evaluator semantics through adapters, shell fragments, or compiler folklore.

That ambiguity is costly across A/B/C/D because it expands review surfaces, weakens explainability, and quietly widens the trusted computing base.

## Decision

1. **No general-purpose evaluator is part of the Derive core or the blessed in-tree package recipe surface.**
   User-authored package/build recipes do not gain ambient loops, user-defined functions, macros, module systems, or hidden imports as product semantics.

2. **The only in-tree native package-recipe direction worth pursuing is the restricted typed pipeline lane already sketched in `RFC-0091`.**
   That lane may grow an explicit step registry later, but it remains step-typed, finite, explicit-input, and policy-checkable rather than a general language runtime.

3. **Rich recipe ecosystems remain adapter/compiler lanes.**
   Ports/pkgsrc importers, apko/melange bridges, Starlark/Nix-like authoring, and shell-heavy external builders may still exist, but only as bounded lanes that emit canonical Derive Lock/Plan/evidence objects and stay killable under Adapter→Shadow→Replace discipline.

4. **Shell remains backend implementation detail, not recipe authority.**
   Tool capsules or compiled plan steps may still run shell or language-specific build tools, but that power is owned by the compiled execution lane, not by a blessed user-authored recipe language.

5. **Capability posture remains explicit.**
   Recipe compilation/evaluation and any future restricted pipeline lane keep ambient network, unbounded imports, and hidden resource reads out by default; fetch remains a separate explicit capability.

## Consequences

- the top-level language question is now closed without pretending the exact restricted pipeline schema is done
- A/B/C/D keep one coherent build-authoring boundary without forking product semantics
- future work narrows to concrete implementation questions:
  - exact restricted step vocabulary
  - exact adapter/import depth
  - exact explain/provenance surfaces for compiled recipe steps
- reviewers can reject “just add a little language” proposals unless they come back as explicit adapter lanes or a narrow RFC-0091 follow-on

## Why this is narrow enough

This ADR does **not** bless a new package format, pick a final step registry, or replace existing builder backends.
It only fixes the authority boundary:

- no general-purpose in-tree package-recipe evaluator
- restricted typed pipeline remains the only native follow-on lane under consideration
- richer recipe ecosystems stay adapter/compiler lanes
- shell stays compiled/backend detail rather than reviewed recipe language authority

That is a small hard decision with high leverage and low subsystem sprawl.
