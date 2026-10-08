# Crate runtime handoff/support-bundle lane boundaries — 2026-03-16

This note exists to keep the archive honest now that the repo has a stronger **compile-time guidance** lane and is adding a distinct **runtime failure handoff** lane.

The question here is not merely how a crate renders an error.
It is:

> “After a runtime failure happens, what structured, redactable material does the crate hand another person or tool?”

## Lane 1: receiver-facing runtime handoff packs

**Proposal:** `P-0513 Crate Runtime Handoff Pack Kit`

This lane should own:

- runtime error receipts,
- panic-path receipts,
- redaction profiles,
- safe-to-share support bundles,
- recovery-step manifests for runtime failures,
- and failure-shape diffs across releases.

The central question is:

> “What runtime failure material can this crate safely hand off, and how is it verified?”

That is different from compile-time guidance packs.

## Lane 2: compile-time / early failure guidance packs

**Proposal:** `P-0512 Crate Guidance Pack Kit`

This lane should own:

- compile-fail guidance,
- `#[diagnostic]`-backed hints,
- proc-macro misuse guidance,
- feature/runtime mismatch guidance before or at build time,
- recipe-backed recovery steps for early failures,
- and support-surface diffs for those guidance paths.

The central question is:

> “What guidance does a chosen crate give before the program successfully runs?”

That is different from `P-0513`, which is about **runtime failure handoff after execution has already started**.

## Lane 3: generic error representation and rendering

**Examples:** `miette`, `eyre`, `ariadne`, `codespan-reporting`, parts of `error-stack`

These crates should own:

- error representation patterns,
- pretty or machine-readable rendering,
- formatter backends,
- and general report presentation.

The central question is:

> “How should errors or diagnostics be represented and rendered?”

That is different from `P-0513`, which is about a **verified handoff contract** with redaction, receipts, and diffs.

## Lane 4: tracing, logging, and observability

**Examples:** `tracing`, `tracing-error`, OpenTelemetry stacks, logging crates

These crates should own:

- emitted runtime telemetry,
- span and event context,
- streaming export,
- backend integrations,
- and broad operational observability.

The central question is:

> “What telemetry do we emit during execution?”

`P-0513` may import telemetry or span context, but it should not become a full observability platform.

## Lane 5: domain-specific doctors and incident bundles

**Examples:** Cargo/build support bundles, local-first incident bundles, protocol-specific conformance kits

These crates should own:

- domain-specific capture formats,
- protocol or build-system diagnosis,
- incident replay artifacts,
- and problem-specific doctor flows.

The central question is:

> “What artifact does this specific domain need to diagnose its own failures?”

`P-0513` is narrower and more cross-cutting: it is the **crate-authored runtime handoff layer** above generic `std`/ecosystem error substrate and below domain-specific labs.

## Lane 6: crate choice and support claims

**Proposals:** `P-0509`, `P-0510`, `P-0511`

These lanes should own:

- task-first crate selection,
- producer-side support claims,
- and shared ecosystem interop profiles.

The central questions are:

- “Which crate should I choose?”
- “What does this crate claim to support?”
- “What shared profile does it fit?”

That is different from `P-0513`, which assumes the crate is already chosen and a runtime failure has already happened.

## Working rule

When a future pass touches crate supportiveness, it must state explicitly whether the new value is about:

1. **which crate to choose**,
2. **what a crate claims to support**,
3. **what shared interop profile a crate fits**,
4. **what compile-time or early-failure guidance a crate provides**,
5. **what runtime failure material a crate hands off**,
6. **how errors are rendered**,
7. or **what telemetry / domain incident bundle is emitted**.

Do not let the archive flatten these into one vague “better DX” bucket.
