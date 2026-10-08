# Crate support-surface boundaries — 2026-03-17

This note exists to keep the archive from collapsing several adjacent receiver-facing crate lanes into one fake “better DX” bucket.
The frontier is now rich enough that this distinction itself is a form of repo hygiene.

## Main split

### P-0512 — Crate Guidance Pack Kit
Use this lane when the user is blocked **at compile time** and needs the smallest supported path forward.
Key objects: guidance authority, recovery origin, recipe fidelity.

### P-0513 — Crate Runtime Handoff Pack Kit
Use this lane when something already failed **at runtime** and the crate should produce a shareable bundle.
Key objects: capture exactness, share safety, handoff fidelity.

### P-0518 — Crate Observability Surface Pack Kit
Use this lane when the question is about **what signals the crate emits**, how they are activated, and how stable their names/semantics are.
Key objects: signal stability, activation recipes, schema/convention posture.

### P-0524 — Crate Example Surface Pack Kit
Use this lane when the user needs the **smallest official path to first success** and needs to know which example path is trustworthy.
Key objects: quickstart paths, environment honesty, output expectations, example-surface diffs.

### P-0525 — Crate Diagnosis Surface Pack Kit
Use this lane when the crate **did not necessarily crash** but is stalling, flooding, going quiet, timing out, or otherwise misbehaving and the user needs an official troubleshooting path.
Key objects: symptom classes, triage origins, signal maps, bundle-safety posture.

## Pairwise guardrails

- **Guidance vs diagnosis**: guidance is about *how to get unstuck from misuse or unsupported compile-time situations*; diagnosis is about *how to reason about live or quasi-live misbehavior once code already runs*.
- **Runtime handoff vs diagnosis**: handoff is about *what bundle to attach after failure*; diagnosis is about *what symptom vocabulary, self-checks, and inspection order exist before or alongside escalation*.
- **Observability vs diagnosis**: observability is about *signal emission contracts*; diagnosis imports those signals into a *symptom-to-action contract*.
- **Examples vs diagnosis**: examples are about *first success*; diagnosis is about *first credible troubleshooting once the happy path no longer holds*.
- **Pathfinder vs examples**: pathfinder chooses *which crate or starter set to adopt*; example surfaces choose *which official path inside that crate is the start*.

## Working rule for future archive edits

If a proposed crate primarily answers one of these questions, keep it in the corresponding lane:

1. “Why does this fail to compile and what is the supported smallest fix?” → **P-0512**
2. “What can I safely hand to another person after runtime failure?” → **P-0513**
3. “What telemetry / traces / metrics / warnings does the crate emit and how do I turn them on?” → **P-0518**
4. “What is the smallest officially supported path to first success?” → **P-0524**
5. “It runs, but something is wrong — what symptoms are recognized, what do I inspect first, and what can I safely capture?” → **P-0525**

## Why this note exists now

The archive has already accumulated enough adjacent support-surface work that forgetting these boundaries would create avoidable churn:

- duplicate proposals,
- fake competition between neighboring lanes,
- support crates that quietly absorb too many concerns,
- and LLM revisions that flatten distinct review objects into one generic “supportiveness” story.

Treat this file as an amnesia resistor whenever work touches compile-time guidance, runtime support bundles, examples, observability, or troubleshooting.
