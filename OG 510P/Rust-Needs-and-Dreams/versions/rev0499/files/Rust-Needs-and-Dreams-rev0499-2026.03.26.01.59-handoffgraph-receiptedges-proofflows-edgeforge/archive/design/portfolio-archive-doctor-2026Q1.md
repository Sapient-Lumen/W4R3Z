## Addendum (rev0436)
The doctor loop now includes the shared source atlas as part of its wired repo-health surface.

Interpretation rule:
- this does **not** turn the atlas into a freshness-renewal engine;
- it does **not** say the doctor can prove a source is currently correct;
- it only says that the repo now treats recurring authority-lane cards as a maintained asset with a thin checker and receipt coverage.

## Addendum (rev0433)
The doctor loop now includes the shared proving-grounds matrix as part of its wired repo-health surface.

Interpretation rule:
- this does **not** turn scenario coverage into freshness renewal;
- it does **not** turn the doctor loop into a pilot verdict engine;
- it only says that the repo now treats the shared proving-grounds corpus as a maintained asset with a thin checker and receipt coverage.

## Addendum (rev0432)
For questions about **how the archive should run a real maintainer pass now that it has queues, specimens, protocols, and validators**, read this note right after `design/portfolio-conformance-validation-2026Q1.md` and `design/portfolio-evidence-renewal-2026Q1.md`.

Interpretation rule:
- this note does **not** promote a new seam;
- it does **not** change the broad ladder or the default portfolio order;
- it exists to answer the missing maintenance question: **what single doctor pass should a steward or LLM run before claiming the canon is in good enough shape to extend or ship?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- and require every serious repo-level pass to distinguish **mechanically checked repo health** from **human-reviewed ecosystem freshness**.

# Design: Portfolio archive doctor and maintenance loop (2026 Q1)

## Goal
The archive can now:
- rank strong seams,
- specify what they should ship,
- stage the portfolio,
- triage additions,
- score pilots,
- renew stale evidence,
- route weaker consumer views,
- maintain specimen examples,
- and validate the thin shared envelope contract.

What it still lacked was one canonical answer to a narrower but increasingly important question:

> once the repo has this much canon and this many maintenance layers, what should a real maintainer pass actually do, what can it verify mechanically, what still needs human review, and what receipt should it leave behind?

This note is the archive's answer to **doctor-loop maintenance**, not frontier promotion.

Read with:
- `design/portfolio-conformance-validation-2026Q1.md`
- `design/portfolio-reference-specimens-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`
- `meta/ARCHIVE_DOCTOR_PROTOCOL.md`
- `meta/EVIDENCE_RENEWAL_PROTOCOL.md`
- `meta/PORTFOLIO_CONFORMANCE_PROTOCOL.md`

## Why this note is needed now
The repo is no longer just a pile of good research notes. It now has enough cross-cutting structure that a future revision can fail in a more boring way: not by inventing the wrong frontier, but by only partially updating the canon and still sounding convincing.

Current Rust signals make a repo-level doctor loop more necessary, not less:

- Rust's 2026 goals overview says goals are a contract, that new goals may only be added when resources are already known, and that accepted goals rely on champions, regular updates, and cross-team coordination. That argues for a repo that leaves behind maintenance receipts, not just elegant strategy prose.
  https://rust-lang.github.io/rust-project-goals/2026/
- The February 2026 program-management update says annual goals now sit beneath longer-lived roadmaps and application areas meant to focus industry funding. That argues for boring, repeatable stewardship loops across multi-quarter work rather than one-off “big idea” bursts.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Rust's March 2026 challenges writeup still frames the ecosystem tax as recurring and practical: choice paralysis, tacit knowledge, async complexity, domain-specific maturity gaps, and resource pain. That means the archive's own maintenance should bias toward evidence-bearing discipline rather than another speculative widening.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says docs remain the canonical reference while editor / agentic / LLM-mediated learning is rising. That means this archive should expect more indirect consumption and therefore needs stronger repo-level checks and clearer receipts.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo's build-analysis goal is explicitly about recording build metadata across invocations, linking related records with a build identifier, and surfacing reviewable report commands. The Cargo 1.94 development-cycle update says `cargo report rebuild`, `cargo report sessions`, and structured logging work are all active. That is exactly the ecosystem direction in which “run the checks and leave a machine-readable receipt” becomes normal.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The libtest JSON goal says people had already come to rely on programmatic output and that the format must evolve with future needs. docs.rs rustdoc JSON says consumers must inspect `format_version`, and crates.io's January 2026 update says its frontend now generates type-safe API clients from the OpenAPI description. Those signals all point in the same direction: machine-readable maintenance receipts should be thin, explicit, and versioned.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
  https://docs.rs/about/rustdoc-json
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

Taken together, those signals say the archive needed one explicit answer for **repo-level maintainer discipline**.

## Headline answer
A serious doctor pass should do five things and keep them visibly distinct:

1. **structure check** — confirm that required canon, protocols, and mirrored files exist;
2. **mechanical check** — run the repo's hard validators and fail if they fail;
3. **queue surfacing** — point maintainers back to the hot human-review queues instead of pretending freshness was solved mechanically;
4. **receipt emission** — write one machine-readable last-run report with status, counts, and follow-up pointers;
5. **scope honesty** — say explicitly what the doctor did *not* prove.

In archive terms, the doctor pass is:
- stronger than “looks fine to me”,
- weaker than a real evidence-renewal pass,
- and complementary to the shared-envelope checker.

## What the doctor is for
The doctor loop exists to answer:
- did the hard repo checks pass,
- are the expected canonical files present,
- is the current revision pointing maintainers back to the right queues,
- and did this revision leave behind a fresh maintenance receipt?

It does **not** answer:
- whether the Rust ecosystem changed materially,
- whether a new frontier should be promoted,
- whether citations in a hot note remain current,
- whether a queued renewal has been reviewed deeply enough,
- or whether a seam-specific artifact family is semantically correct beyond the thin shared contract.

## The doctor pass, phase by phase

### 1) Canon presence phase
Confirm the files that make the repo navigable and reviewable are present.
At minimum, the doctor should verify the presence of:
- root canon: `INDEX.md`, `PRIORITIES.md`, `RESEARCH_LOG.md`, `STRATEGIC_FRONTIER.md`, `AGENTS.md`;
- core meta notes: `meta/CANONICAL_WORKING_SET.md`, `meta/ACTIVE_FRONTIER.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/ARCHIVE_MANIFEST.md`;
- doctor protocol and latest receipt;
- and the current validator scripts the repo claims to rely on.

Failure here is hard failure because a missing canonical file breaks maintainability before any strategic argument starts.

### 2) Mechanical validation phase
Run the repo's hard-check surfaces.
In the current archive that means:
- `python tools/check_cargo_report_pack_contract.py`
- `python tools/check_portfolio_envelope_contract.py`

The doctor should treat those as **required** checks, not advisory suggestions.
The point is not to pretend the repo is fully machine-checkable; the point is to keep the machine-checkable part from drifting silently.

### 3) Queue surfacing phase
After hard checks pass, the doctor should still point back to human-review queues such as:
- `meta/CANONICAL_RENEWAL_QUEUE.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`

This phase should produce **follow-up pointers**, not verdict laundering.
A passing doctor report must still be able to say, in effect: “repo health passed, but freshness and prioritization remain human work.”

### 4) Receipt phase
The doctor should leave one machine-readable receipt, currently `meta/ARCHIVE_DOCTOR_LAST_RUN.json`.
That receipt should include:
- revision identity;
- UTC generation time;
- required-file status;
- named check results;
- small corpus counts that help spot accidental shrinkage or growth;
- queue pointers for manual follow-up;
- and explicit limitations.

The receipt should be useful for diffing consecutive revisions, not just for celebratory logging.

### 5) Scope-honesty phase
The doctor must say explicitly what it did **not** establish.
At minimum:
- it did not refresh external citations;
- it did not rerank seams;
- it did not validate seam-local payload semantics beyond the thin checks already wired in;
- and it did not make a stale note current by assertion.

## Required hard failures vs required warnings

### Hard failure conditions
The doctor should fail when:
- a required canonical file is missing;
- a required validator exits non-zero;
- the last-run receipt cannot be written;
- or the repo claims a required doctor asset exists but it does not.

### Required warnings / reminders
The doctor should warn or remind when:
- renewal queues still require human review;
- queue pointers exist but there is no claim they were processed in this run;
- counts changed in a way that deserves human attention but is not automatically wrong;
- or a maintainer may be tempted to treat “doctor passed” as “research fresh”.

## Default command shape
The repo now has one canonical entrypoint:

`python tools/archive_doctor.py --write meta/ARCHIVE_DOCTOR_LAST_RUN.json`

The tool should:
- run the required checks,
- emit JSON to stdout,
- optionally write the same JSON to a path,
- and exit non-zero on hard failure.

## Why this is a worthy repo increment
This note does not make the archive more glamorous.
It makes it more **operable**.

That is strategically worthwhile because the Rust ecosystem is increasingly moving toward reviewable, machine-usable, evolving surfaces rather than one-shot static interfaces. A repo that argues for evidence-bearing seams should itself model a thin evidence-bearing maintenance loop.

## Anti-goals
Do **not** let the archive doctor become:
- a fake freshness oracle,
- a universal validator for every seam payload,
- a CI empire with dozens of brittle rules,
- or a self-congratulatory badge that says “all good” while renewal queues burn.

## What should happen next
For now, the doctor loop should stay thin:
- check presence,
- run the hard validators,
- emit one receipt,
- point back to manual queues.

Only after the repo accumulates more genuinely stable machine-checkable layers should the doctor absorb more checks.

## Default archive conclusion after this addition
- **Build-State Evidence** remains the strongest one-project answer overall.
- The strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**.
- **Native Edge Contract** remains the active specialist frontier.
- This revision adds one canonical answer for **how a maintainer or LLM should run a real archive-health pass and leave a receipt**.
