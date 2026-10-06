# ADR-0089: Fuzz target classes and flake-aware promotion boundary

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already had the right raw ingredients for useful fuzzing:
`docs/274-continuous-fuzzing-farm.md` framed fuzzing as receipted evidence,
`docs/275-root-cause-certificates-and-bisection.md` explained how failures can become localized instead of heroic archaeology,
and `docs/376-parser-surface-registry-and-fuzz-gates.md` / `docs/406-uapi-fuzz-descriptors-and-conformance.md` tied fuzz work to registry surfaces.

What remained fuzzy was **what promotion actually keys on**.
Without a hard decision here, continuous fuzzing drifts toward the same failure modes seen elsewhere:

- dashboards optimize for raw coverage percentages because they are easy to graph,
- crash triage mixes reproducible and flaky failures together,
- release gates become hand-wavy (“we fuzz this area a lot”) instead of mechanically reviewable,
- and regression localization still depends on heroics because the archive never fixed which fuzz outcomes are authoritative enough to gate anything.

The archive already has typed evidence, replay lanes, and product profiles.
We only needed a smaller contract for fuzz evidence and crash reproducibility.

## Decision

DeriveBSD accepts a narrow **fuzz target-class and flake-aware promotion boundary**:

1. **`fuzz.receipt` is evidence-only.**
   It records what target class/id was fuzzed, with which harness, runner, corpus, and sandbox boundary, plus a compact result summary.
   It does not become release authority on its own.

2. **`crash.case` is the canonical minimized replay artifact for fuzz-discovered failures.**
   It binds the target, the producing `fuzz.receipt`, one or more reproducers, a normalized crash signature, and an explicit reproducibility status.

3. **Promotion gates key on required target classes and open `crash.case`s, not raw coverage percentages.**
   Coverage summaries remain useful evidence for gap-finding and corpus quality, but a bare line/edge/block percentage is not the core release decision surface.

4. **Flaky failures stay triage evidence until they become explicit `crash.case` states.**
   `fuzz.receipt` must summarize reproducible-case counts separately from flake-suspect counts, and `crash.case.reproducibility.status` must say `stable`, `flaky`, or `unreproduced`.
   Root-cause or promotion workflows may treat those classes differently, but they may not silently collapse them into one bucket.

5. **The default fuzz posture is product-shaped.**
   A–D keep one archive but do not pretend they need identical default gates:
   - **A / fleet host:** required classes emphasize `uapi`, `parser`, and `driver` surfaces for shipped trusted-plane code.
   - **B / workstation:** required classes emphasize `importer`, `broker`, and `parser` surfaces that face humans and foreign content.
   - **C / general OS:** shipped host/importer classes are required for core deliverables, while broader compatibility surfaces remain advisory or adapter-scoped.
   - **D / appliance_factory:** approved production target sets, retained corpora, and zero open production-relevant reproducible cases are the default posture.

## Meaning in practice

### Coverage stays useful, but not authoritative

Coverage reports, introspector output, and corpus growth still matter.
They are how teams discover blind spots and prioritize harness work.
But the archive now says one clear thing:
**coverage is guidance; target-class completion and crash-case state are the gate surface.**

### Reproducibility is explicit

A crash that only happens under unstable timing or one-off state coincidences is still important,
but the archive should not pretend it is the same thing as a minimized replayable bug.
`crash.case` now carries that distinction directly.

### Root-cause work gets cheaper

`rootcause.certificate` flows can now distinguish:
- stable reproducible failures,
- flaky but recurring failures,
- unreproduced observations,
- and pure infrastructure failure.

That keeps blame workflows from over-claiming certainty.

## Consequences

### Positive

- Fuzzing becomes a mechanical release/input-quality lane instead of a vanity dashboard.
- Product shapes can keep different default gates without forking the archive.
- Crash triage is less likely to confuse flaky observations with replayable bugs.
- Coverage summaries remain available for operator and engineering insight without becoming fake authority.

### Negative / trade-offs

- This adds two more stable artifact kinds (`fuzz.receipt`, `crash.case`).
- Some existing docs that used “fuzzing evidence” loosely now need sharper wording.
- The archive still does not decide exact farm sizing, retention budgets, or every target id taxonomy.

## Non-goals

This ADR does **not** decide:

- the final farm scheduler or dashboard UX,
- exact numeric execution budgets per target,
- exact retention windows for every corpus or crash severity,
- or the full long-term target-id namespace beyond the stable target classes used in v0.

Those remain implementation and future tuning questions.

## Why this shape

The coherence win is not inventing a giant fuzz-control subsystem.
It is deciding that the archive already has enough pieces,
provided it says one clear thing:

**promotion gates care that the right target classes were exercised and that new failures became explicit replayable `crash.case` objects with reproducibility state; coverage percentages stay evidence, not authority.**
