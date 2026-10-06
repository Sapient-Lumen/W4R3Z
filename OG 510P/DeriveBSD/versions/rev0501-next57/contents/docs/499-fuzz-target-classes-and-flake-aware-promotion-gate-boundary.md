# Fuzz target classes and flake-aware promotion-gate boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

DeriveBSD already had continuous fuzzing, replayable crash artifacts, and root-cause certificates.
This doc makes one small but important decision: **promotion gates key on target classes and explicit crash-case state, not raw coverage percentages.**

See also:
- ADR: `adrs/ADR-0089-fuzz-target-classes-and-flake-aware-promotion-boundary.md`
- continuous fuzzing lane: `docs/274-continuous-fuzzing-farm.md`
- bisection / blame lane: `docs/275-root-cause-certificates-and-bisection.md`
- parser fuzz gates: `docs/376-parser-surface-registry-and-fuzz-gates.md`
- UAPI fuzz descriptors: `docs/406-uapi-fuzz-descriptors-and-conformance.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

The archive already knew that fuzzing matters.
What it did not say crisply enough was **what counts as gate-worthy evidence**.
That gap is expensive:

- teams optimize for graph-friendly coverage percentages because they are easy to explain,
- flaky failures get mixed together with replayable bugs,
- dashboards imply confidence that nobody can reproduce locally,
- and regressions still require heroics because the archive never names the minimal promotion surface.

DeriveBSD already has the right pieces to avoid this.
We just need to route the official workflow through them.

## The official fuzz-evidence boundary

1. **`fuzz.receipt` is evidence-only.**
   It binds the target class/id, harness digest, runner digest, sandbox boundary, corpus inputs, and compact outcome summary.

2. **`crash.case` is the canonical minimized replay artifact.**
   It binds the target, the producing `fuzz.receipt`, reproducers, normalized signature, and reproducibility state.

3. **Coverage summaries are advisory evidence.**
   `coverage_summary_digest` is useful for understanding harness quality and blind spots, but coverage percentages are advisory and must not become the core release authority surface.

4. **Promotion gates key on target classes + crash-case state.**
   The mechanical questions are:
   - did the required target classes run?
   - did they emit fresh `fuzz.receipt`s?
   - are there new open `crash.case`s for those classes?
   - are those cases `stable`, `flaky`, or `unreproduced`?

5. **Flake accounting is explicit.**
   `fuzz.receipt.result_summary` carries reproducible-case counts separately from flake-suspect counts.
   `crash.case.reproducibility.status` carries the minimized replay verdict.
   Root-cause or promotion tooling can then be strict without lying about confidence.

## Minimal artifact changes

### `fuzz.receipt`

The v0 object is intentionally small.
It should answer:

- what target class/id was fuzzed?
- which harness / runner / sandbox was used?
- which corpus snapshot seeded the run?
- how much execution happened?
- how many new crash cases were found?
- how many were reproducible versus flaky?

### `crash.case`

A crash case is only useful if it is portable and bounded.
The object should capture:

- the source target id/class and target digest
- the producing `fuzz.receipt`
- minimized reproducers
- a normalized crash signature
- explicit reproducibility state (`stable`, `flaky`, `unreproduced`)
- a safe replay profile (default: disposable no-network compartment)

This keeps “download case → replay case” a normal workflow instead of a dashboard archaeology ritual.

## Product-shape defaults

### A) Secure fleet host

Default required classes emphasize:
- `uapi`
- `parser`
- `driver`

The gate cares about stable shipped host surfaces, not vanity coverage percentages.
New stable crash cases in those classes should block normal promotion until triaged or waived through the proper stronger lane.

### B) Secure workstation

Default required classes emphasize:
- `importer`
- `broker`
- `parser`

The main risk is foreign content and mediated boundary handling, not “how many lines did the dashboard color green”.

### C) General-purpose OS

Core shipped host/importer surfaces still need fuzz evidence.
Broader compatibility and adapter territory remain viable, but the archive names them as such instead of pretending every compatibility surface is part of the default gate.

### D) Appliance / factory / regulatory

The default posture is the strictest:
- approved production target sets are explicit,
- retained corpora/crash artifacts are normal,
- and zero open production-relevant reproducible crash cases is the default expectation.

## Root-cause and blame posture

This boundary intentionally helps `docs/275-root-cause-certificates-and-bisection.md`.
Flake-aware blame is now the default rule:

- stable reproducible `crash.case`s may trigger automated bisection
- flaky cases stay triage evidence until their state is improved
- infrastructure failure (`infrastructure-failed`) is not a product bug verdict

That keeps automation useful without letting it over-claim certainty.

## What this does not decide

Still open:

- exact numeric exec/time budgets per target class
- exact corpus/crash retention windows per severity or product line
- exact UI for dashboarding, suppression, or waiver review
- the long-term detailed target-id taxonomy beyond the stable v0 class set

Those are implementation or future RFC questions.
The boundary itself is now fixed.

## Design cues from current systems

The current ecosystem pattern is clear and stable:

- syzkaller and syzbot make corpus, crash reproduction, and manager topology first-class parts of the workflow.
- syzbot explicitly treats reproducers as best-effort, which is exactly why reproducibility state must be named rather than assumed.
- OSS-Fuzz and Fuzz Introspector treat coverage and reachability as useful guidance for improving fuzzers, not as a complete statement of release readiness.

DeriveBSD should keep the same instinct while translating it into its own typed artifact model:
required target classes, explicit replayable crash cases, and flake-aware gate summaries.

Last updated: 2026-03-07r228
