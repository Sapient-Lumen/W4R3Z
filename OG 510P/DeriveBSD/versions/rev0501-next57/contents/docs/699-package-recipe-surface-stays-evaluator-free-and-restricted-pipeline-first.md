# Package recipe surface stays evaluator-free and restricted-pipeline-first

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability  
**Patterns:** Adapter→Shadow→Replace, Plan→Apply→Receipt

The archive already knew two things:

- the Derive core should not execute user code during evaluation (`docs/83-evaluator-minimalism.md`), and
- richer authoring frontends should compile to canonical JSON instead of becoming authority (`docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`).

What still cost too much attention was the build/package side of the same question:

> when people describe **how to build software**, how much language is allowed before the recipe runtime becomes the real product?

This doc fixes that boundary.

See also:
- ADR: `adrs/ADR-0289-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`
- restricted-pipeline RFC: `rfcs/RFC-0091-declarative-image-pipelines.md`
- build-pipeline lesson: `docs/134-declarative-image-pipelines-apko-melange.md`
- evaluator boundary: `docs/83-evaluator-minimalism.md`
- frontend boundary: `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`

## Accepted boundary

The package recipe surface for the core product stays **evaluator-free**.

That means:

- no blessed in-tree general-purpose recipe language
- no ambient loops/functions/macros/modules as authoritative package semantics
- no hidden importer/runtime that quietly becomes more important than Lock/Plan
- no “shell is the real spec” posture

Instead, DeriveBSD keeps one narrow split:

- **native in-tree follow-on lane:** restricted typed pipelines only (`RFC-0091`)
- **all richer recipe ecosystems:** adapter/compiler lanes only

That native lane is now narrowed one step further too: `docs/700-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md` fixes that the first restricted pipeline cannot hide a general evaluator behind a generic authoritative `run` / `script` step.

## Restricted typed pipeline is the only native follow-on lane

`RFC-0091` remains the place to decide the exact native build-recipe follow-on.
But this archive now makes one hard narrowing cut:

if DeriveBSD adds a native package recipe authoring lane, it must be a **restricted typed pipeline** rather than a general evaluator language.

So future native recipe work may decide:

- exact step vocabulary
- exact step/input/output schema
- exact explain/provenance receipts
- exact compiler/backend mapping

But it does **not** reopen whether the product should grow an in-tree Nix-like, Starlark-like, or shell-like evaluator.

## Rich recipe ecosystems remain adapter/compiler lanes

This is where practicality stays compatible with coherence.

DeriveBSD may still ingest or interoperate with richer build ecosystems:

- ports/pkgsrc importers
- apko/melange bridges
- Starlark/Nix-like external compilers
- shell-heavy external packaging systems

But those lanes must compile or translate into explicit Derive objects and evidence:

- canonical Lock/Plan inputs
- explicit capability posture
- receipts for source/import/translation/build steps

The archive refuses to let those ecosystems become hidden authority just because they are convenient or already widespread.

## Shell stays backend detail, not recipe authority

Builders will still run real tools, real compilers, and sometimes shell.
That is not the same thing as blessing shell as the package recipe language.

The reviewed recipe boundary stays on typed authoring + compiled plan objects.
Any shell or language-specific execution lives downstream in:

- tool capsules
- compiled plan steps
- adapter imports
- backend execution receipts

This keeps the archive honest about where expressive power exists.

## Capability posture is part of the boundary

Modern configuration/build tools often grow imports, registries, embedded files, external readers, and HTTP-aware dependency mechanisms.
Those can be useful, but they are also how “authoring convenience” quietly becomes a second evaluator/runtime.

So DeriveBSD keeps the default posture explicit:

- no ambient network for recipe evaluation/compilation
- no hidden unbounded imports as product semantics
- fetch remains a separate explicit capability
- richer adapter lanes must state their import/resource posture in evidence, not smuggle it in through folklore

## Product-shape fit

- **A / fleet host:** keeps the highest-assurance build story small enough to review and govern.
- **B / workstation:** keeps power-user/package ergonomics possible through adapters without letting workstation convenience redefine the core build model.
- **C / general-purpose OS:** preserves breadth by allowing adapters and ecosystem bridges, while keeping the native center small and explainable.
- **D / appliance / regulatory:** keeps audit and rebuildability portable because the authoritative recipe boundary stays typed and bounded.

## Why this is the right small hard decision

Choosing an exact step registry today would be premature.
Leaving the language boundary open would be worse.

This cut solves the more expensive problem first:

- the package recipe language question is no longer open-ended
- the native direction is narrowed to restricted typed pipelines
- richer ecosystems stay compatible but subordinate
- future work can argue about step vocabularies and adapters instead of re-litigating whether the real product is “some scripting language plus folklore”

## Related docs

- `adrs/ADR-0289-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`
- `docs/83-evaluator-minimalism.md`
- `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`
- `docs/134-declarative-image-pipelines-apko-melange.md`
- `rfcs/RFC-0091-declarative-image-pipelines.md`
- `docs/700-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md`
- `docs/266-open-questions-and-risk-register.md`

Last updated: 2026-03-23r431
