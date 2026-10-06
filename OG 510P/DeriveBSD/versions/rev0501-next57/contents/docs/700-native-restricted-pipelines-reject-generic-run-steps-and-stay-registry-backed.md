# Native restricted pipelines reject generic run steps and stay registry-backed

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability  
**Patterns:** Adapter→Shadow→Replace, Plan→Apply→Receipt

`docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md` already fixed the large language-boundary question.
This page closes the next smaller loophole that would otherwise undo it:

> the native restricted pipeline lane does **not** get a generic authoritative `run` / `script` / opaque-command step.

If DeriveBSD allowed that, the native “restricted pipeline” would just become a renamed package DSL with shell-shaped folklore semantics.

See also:
- ADR: `adrs/ADR-0290-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md`
- package-recipe authority boundary: `docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`
- restricted-pipeline RFC: `rfcs/RFC-0091-declarative-image-pipelines.md`
- build-pipeline lesson: `docs/134-declarative-image-pipelines-apko-melange.md`

## Accepted boundary

The native restricted pipeline lane stays **registry-backed and typed**.

That means:

- no authoritative native `run` step
- no authoritative native `script` step
- no “array of commands” step whose semantics are whatever the backend happened to do
- no reviewed recipe surface that depends on hidden shell/runtime folklore

Instead, each native pipeline step must:

- declare a finite `step_kind` from an explicit registry
- carry typed parameters for that step kind
- expose capability/resource posture that policy and explain surfaces can reason about
- remain narrow enough that a receipt can say what happened without replaying a shell session

## Why the `run` escape hatch is too expensive

A generic `run` step looks convenient because it postpones design work.
In practice it reintroduces the whole problem the archive just cut away:

- the command language becomes the real product
- policy gates lose semantic visibility
- diff/review collapses to command text and tool-image folklore
- reproducibility/debugging start depending on backend quirks instead of typed intent

The archive would rather keep some workflows in adapters for longer than pretend a disguised shell step is “restricted”.

## Where imperative power is still allowed

This is **not** a claim that shell or imperative tooling disappears from builds.
It only says that imperative power does not become the reviewed native recipe contract.

Imperative logic may still exist inside:

- tool capsules
- builder backends
- adapter/compiler lanes
- imported foreign recipe ecosystems

But when it does, the native reviewed surface must still stay on explicit compiled plan objects plus receipts.

## What remains open

This cut intentionally does **not** pick the whole first registry.
That work still belongs in `RFC-0091`.
The remaining questions are implementation-shaped now:

- which initial `step_kind` values are worth standardizing first
- which typed parameters each step kind needs
- which capability/evidence fields each step kind must expose
- which existing ecosystems stay adapters rather than native steps

## Product-shape fit

- **A / fleet host:** keeps the highest-assurance package lane small enough to audit.
- **B / workstation:** allows pragmatic adapters without letting convenience redefine native authority.
- **C / general-purpose OS:** preserves breadth through adapters while keeping the native center reviewable.
- **D / appliance / regulatory:** keeps recipe review/export/audit on typed steps instead of opaque command folklore.

## Related docs

- `adrs/ADR-0290-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md`
- `docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`
- `docs/134-declarative-image-pipelines-apko-melange.md`
- `rfcs/RFC-0091-declarative-image-pipelines.md`
- `docs/83-evaluator-minimalism.md`
- `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`

Last updated: 2026-03-23r431
