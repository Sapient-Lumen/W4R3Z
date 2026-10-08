# Epic crate support-envelope framework — 2026-03-25

This note answers the archive’s recurring practical question directly:

**What should a worthy crate provide other people?**

The short answer is:
it should provide a compact, reviewable **support envelope** that another team can adopt without inheriting the author’s unstated assumptions.

## The support-envelope test

A worthy crate should provide all of the following in some bounded first release:

1. **Decision help**
   - what repeated question it answers;
   - for which receiver class;
   - under what evidence floor.

2. **Imported truth**
   - which official surfaces it reads;
   - which project-local inputs it needs;
   - what remains manual.

3. **Machine-readable outputs**
   - at least one packet family suitable for CI, review, or archival handoff.

4. **Human-readable summary**
   - a concise explanation of the conclusion,
   - the support ceiling,
   - and the next action.

5. **Recheck story**
   - what invalidates the answer,
   - what gets rerun,
   - and what artifact supersedes the old one.

6. **Refusal boundary**
   - what the crate will not certify,
   - and how that refusal is surfaced.

7. **Scenario corpus**
   - at least one success path,
   - one degraded-but-honest path,
   - one recheck-trigger path,
   - and one refusal path.

If a proposal cannot say all seven things, the archive should keep treating it as interesting but not yet worthy.

## Service-level ladder for missing crates

This archive now benefits from a simple service-level ladder.

### **SL0 — observational**
The crate can import and display ecosystem signals.
Useful, but not yet enough.

### **SL1 — reproducible local**
Another team can rerun the crate locally and reproduce the same packet shape.

### **SL2 — pinned witness**
The crate can freeze a basis and later prove what it actually looked at.

### **SL3 — support envelope**
The crate can explain a bounded support claim across hosted/local/target/toolchain or similar reality surfaces.

### **SL4 — continuity**
The crate can reopen, revalidate, and transition prior answers on named triggers.

### **SL5 — adoption contract**
The crate can be handed off between people or teams without losing the meaning of the prior result.

A worthy near-term crate should usually aim for **SL2–SL4** in `0.1`, not pretend to start at universal automation.

## Design rules

### 1. Imported truth beats self-description
Prefer:
- crates.io,
- docs.rs,
- Cargo,
- rustdoc JSON,
- StableMIR,
- pinned local project state,
- and explicit manual receipts

over informal README marketing or generic popularity stories.

### 2. Small honest packets beat giant dashboards
The first useful release should usually export a small packet family and one short markdown summary.
Do not begin with an “all ecosystem intelligence platform”.

### 3. Refusal is a feature
A good crate should say:
- “unknown”,
- “not enough evidence”,
- “hosted docs only”,
- “cross-compiled, not validated”,
- “debug support only on this matrix”,
- or similar bounded language
instead of overclaiming.

### 4. Support language must be attached to a corpus
Do not say “supports Windows”, “supports async debugging”, “safe for offline”, or “good for regulated use”
unless the crate also ships the scenario family that justifies the wording.

### 5. Handoff matters
The packet must help the next person, not only the first operator.

## Practical application to current leaders

### **P-0509 + P-0536**
First strong `0.1`:
- one decision packet,
- one frozen witness basis,
- one short offer summary,
- one recheck trigger file.

Why worthy:
- directly answers current crate-choice pain,
- composable across many domains,
- and built on surfaces that already exist today.

### **P-0472 + P-0484**
First strong `0.1`:
- one docs/build parity report,
- one target/toolchain support report,
- one support ceiling note.

Why worthy:
- turns “it built on docs.rs” or “it probably supports this target” into bounded claims.

### **P-0535**
First strong `0.1`:
- one trigger intake,
- one revalidation report,
- one transition plan.

Why worthy:
- makes old answers survive advisories, releases, yanks, and parity changes.

### **P-0486**
First strong `0.1`:
- one debugger matrix packet,
- one async-debugging claim ceiling,
- one support summary with explicit OS/debugger/version scope.

Why worthy:
- current official debugging signals still emphasize cross-debugger and cross-OS variance.

## Anti-patterns

Do not promote a proposal just because it sounds grand:

- “the one true Rust web framework”
- “the Rust GUI savior”
- “the ML umbrella crate”
- “enterprise Rust platform”
- “universal crate ranking AI”

Those may describe appetites, not maintainable first releases.

## Better question for future passes

Before promoting a lane, ask:

**What exact bounded support envelope will another team receive on day one, and what packet proves it?**
