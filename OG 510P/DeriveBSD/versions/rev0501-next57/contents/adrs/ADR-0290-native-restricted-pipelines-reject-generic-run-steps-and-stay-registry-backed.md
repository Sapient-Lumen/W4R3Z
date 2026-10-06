# ADR-0290: Native restricted pipelines reject generic run steps and stay registry-backed

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0289` fixed the big package-recipe language question:

- no blessed in-tree general-purpose evaluator,
- native follow-on work stays on the restricted typed pipeline lane,
- richer ecosystems remain adapter/compiler lanes.

That still leaves one smaller but implementation-blocking loophole open in `rfcs/RFC-0091-declarative-image-pipelines.md`:

> could the “restricted pipeline” quietly grow a generic `run`, `script`, or opaque command-array step and thereby smuggle arbitrary recipe authority back into the native reviewed surface?

If the answer is yes, the archive has only renamed the old problem.
A generic imperative step would quickly become the real package language:

- reviewers would end up reading shell/command folklore instead of typed recipe objects,
- policy would lose the ability to reason about capability posture by step kind,
- explainability would collapse back toward “some command ran in some tool image”, and
- A/B/C/D would inherit a wider recipe/runtime TCB than the archive just agreed to keep out.

## Decision

1. **The native restricted pipeline lane must not expose a generic authoritative `run`, `script`, or arbitrary-command step.**
   There is no blessed reviewed step whose semantics are “execute these commands and trust the result”.

2. **Authoritative native pipeline steps stay registry-backed and typed.**
   Each step in the native lane must identify a finite `step_kind` from an explicit registry and carry typed parameters whose capability/resource posture is reviewable.

3. **Imperative power stays downstream in bounded backends, not in reviewed recipe authority.**
   Tool capsules, builders, compilers, or adapters may internally use shell or richer runtimes, but that power belongs to backend implementation plus receipts, not to the native reviewed recipe contract.

4. **When a workflow truly needs arbitrary imperative logic, it leaves the native lane.**
   That work must use an explicit adapter/compiler/import lane rather than silently widening the native restricted pipeline surface.

## Consequences

- `RFC-0091` can now evolve toward a concrete step registry without carrying a disguised shell escape hatch.
- Future debates narrow to useful implementation questions:
  - which step kinds belong in the first registry,
  - which parameters and evidence each step kind needs,
  - and which existing ecosystems are worth importing as adapters.
- Reviewers gain a mechanical line: proposals that add native `run`/`script` authority are out of bounds unless they come back as adapter lanes or a fresh ADR/RFC that explicitly reopens this boundary.

## Why this is narrow enough

This ADR does **not** pick the full first step vocabulary.
It does **not** define the final pipeline schema.
It only closes the most dangerous loophole left after ADR-0289:

- native restricted pipelines stay registry-backed,
- no generic reviewed `run`/`script` step,
- arbitrary imperative logic remains adapter/backend territory.

That is a small hard decision with immediate leverage for specs and implementation planning.
