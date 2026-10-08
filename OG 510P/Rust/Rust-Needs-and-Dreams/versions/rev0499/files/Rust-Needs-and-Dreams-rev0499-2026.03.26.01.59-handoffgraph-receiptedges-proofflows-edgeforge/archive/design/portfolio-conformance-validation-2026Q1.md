# Design: Portfolio Conformance Validation (2026 Q1)

## Goal
Turn the archive's shared-grammar, consumer-routing, and specimen-corpus ideas into a **thin conformance layer** that can be checked mechanically.

The repo now has strong cross-cutting notes for:
- artifact conventions;
- execution sequencing;
- proposal triage;
- pilot evaluation;
- evidence renewal;
- consumer routing;
- and reference specimens.

What it still lacked was one practical answer to a narrower but now unavoidable question:

> if the archive already knows what honest packs, briefs, diffs, verify receipts, and lineage receipts should *mean*, what should a validator actually be allowed to enforce now, and what should remain seam-specific judgment rather than fake universal schema?

This note answers **conformance / validator scope**, not frontier promotion.

Read with:
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-consumer-routing-2026Q1.md`
- `design/portfolio-reference-specimens-2026Q1.md`
- `meta/PORTFOLIO_CONFORMANCE_PROTOCOL.md`
- `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- `specimens/portfolio-envelope-v0/README.md`

## Why this note is needed now
Fresh Rust signals keep pushing toward more machine-usable surfaces, while also making it obvious that those surfaces evolve and need bounded compatibility promises.
That is exactly when the archive needs a validator-scope note instead of more prose-only agreement.

- Rust's March 2026 challenges writeup says the ecosystem tax is often **choice paralysis** and **tacit knowledge**, not merely lack of crates.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Cargo's build-analysis goal is explicitly about recorded build metadata and reviewable reporting, and it says the prototype may store JSON blobs to allow schema evolution without prematurely freezing a stable format.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo's January 2026 development-cycle note says structured logging is active work and explicitly calls out the data schema plus possible unification with Cargo's JSON output.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The libtest-JSON goal says people already rely on programmatic output and that the format must support both expected future needs and unexpected evolution.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- docs.rs rustdoc JSON now exists as a hosted machine-readable surface, but it explicitly warns that `format_version` matters and that historical coverage is incomplete.
  https://docs.rs/about/rustdoc-json
- The Rustc Librarification / `rustc_public` work is explicitly about a public, SemVer-compliant compiler-facing API for tools that need stronger guarantees.
  https://rust-lang.github.io/project-stable-mir/
- crates.io's January 2026 update says its new frontend generates type-safe API client code from the published OpenAPI description, which is another sign that typed machine contracts are becoming normal ecosystem infrastructure.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

Taken together, those signals say the archive should stop at neither “have shared grammar” nor “have example files”.
It should also say **what the first validator is actually allowed to enforce**.

## Headline answer
The right answer is **not** a universal schema empire.
It is a **thin portfolio-envelope conformance checker** that enforces only the archive's cross-cutting honesty rules.

In plain terms:

> validate the shared honesty spine, role-specific minimums, lineage/escalation discipline, and specimen/fixture sync; leave seam payload semantics to seam-specific packs, importers, and future seam-local validators.

That checker should be:
- **small** enough to understand in one file;
- **strict** about contradictions in authority / lossiness / lineage posture;
- **modest** about seam-specific payload meaning;
- and **fixture-backed** so future revisions can prove both success and failure cases.

## What the conformance layer should check
A worthy first validator should enforce five kinds of truth.

### 1) Shared honesty spine is present
Every portfolio-envelope artifact should carry the archive's outer honesty fields.

At minimum, the checker should require:
- `schema_family`
- `specimen_role`
- `seam`
- `subject`
- `scope`
- `authority`
- `freshness`
- `partiality`
- `imports`
- `attachments`
- `payload`
- `lineage`
- `handoff`

This is the thin layer the archive actually owns across seams.

### 2) Role-specific minimums are real
The validator should not try to understand every seam payload.
But it should know the minimum honesty requirements for each shared role.

Examples:
- a **canonical pack** should not claim a lossy handoff budget;
- a **routed brief** should declare allowed decisions, prohibited decisions, and an escalation target;
- a **verify receipt** should expose a verdict plus prohibited conclusions;
- a **diff** should name both comparison sides;
- a **lineage receipt** should say what transform occurred and what truths were preserved vs omitted.

That is strong enough to prevent fake authority while still leaving seam meaning local.

### 3) Lineage and escalation discipline hold
The archive already says derived views are children, not quiet replacements.
A first validator should enforce that.

In practice, that means:
- non-canonical artifacts should usually name at least one parent;
- weaker views should carry a non-empty escalation target;
- and consumer-facing slices should not silently claim canonical strength.

### 4) Positive and negative examples stay in sync
A shared contract checker is only credible if it exercises both:
- positive specimens that should pass; and
- negative fixtures that should fail for named reasons.

This matters for humans and LLMs alike.
Without negative fixtures, future revisions tend to preserve shape while quietly breaking posture.

### 5) Hard rules stay separate from advisory style
The validator should draw a bright line between:
- **hard failures** that mean the artifact is dishonest or under-specified; and
- **advisory guidance** that may be desirable but should not block revision flow.

Hard failures include things like:
- missing honesty fields;
- canonical packs claiming lossy handoff;
- routed briefs with no escalation target;
- child artifacts with no lineage parent.

Advisory concerns include things like:
- naming polish;
- field ordering;
- optional richer attachments;
- or seam-specific depth that the cross-cutting checker cannot own.

## What a worthy contribution would look like in theory
If someone were building the archive's cross-cutting glue for real, the worthy contribution would look like:

1. a **small contract checker** for the shared portfolio envelope;
2. a **negative fixture set** that proves common honesty failures are actually caught;
3. a **protocol** saying when changes require specimen refresh, fixture refresh, or checker refresh;
4. a **hygiene entry point** that lets future maintainers and LLM edits run one obvious command;
5. and a clear statement that **seam payload validation belongs to seam-local tools**, not to this cross-cutting checker.

That is buildable.
It is also much more honest than pretending the archive should jump straight to one frozen mega-schema.

## What it should look like in practice
A practical first implementation should include:
- `tools/check_portfolio_envelope_contract.py`
- `meta/PORTFOLIO_CONFORMANCE_PROTOCOL.md`
- `fixtures/portfolio-envelope-v0/README.md`
- `fixtures/portfolio-envelope-v0/portfolio-envelope-hygiene-checks.json`
- and a small `fixtures/portfolio-envelope-v0/invalid/` directory.

The checker should:
- validate the passing examples in `specimens/portfolio-envelope-v0/`;
- confirm that the negative fixtures fail for the expected reasons;
- and report pass/fail in plain language.

The checker should **not**:
- validate full seam payload semantics;
- require one universal JSON schema for all roles;
- or pretend that a passing conformance run means the underlying evidence is correct.

## Non-goals
This note is **not** asking for:
- a universal archive schema that owns every seam payload;
- a promise that one checker can validate Build-State, Semantic Context, Package Intake, and Migration semantics end to end;
- a stable forever role set with no future widening;
- or a fake claim that validators eliminate the need for human review.

The goal is much smaller:
**make the archive's cross-cutting honesty rules mechanically checkable without swallowing seam-specific truth.**

## Recommended archive move
Treat this as a **deepening + hygiene** addition.
Do **not** promote a new frontier.
Do **not** change the broad ladder.

Instead:
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep **Native Edge Contract** as the active specialist frontier;
- keep **Adoption Navigation Contract** as the strongest anti-tacit-knowledge answer;
- keep **Package Intake Gateway** as the most underappreciated operational seam;
- keep **Semantic Context Contract** as the hidden multiplier;
- and add one canonical answer for **what shared-grammar rules a validator may actually enforce before future tools or LLM edits claim an artifact is well-formed**.

## Immediate repo consequence
The repo should now maintain:
- `design/portfolio-conformance-validation-2026Q1.md`
- `meta/PORTFOLIO_CONFORMANCE_PROTOCOL.md`
- `fixtures/portfolio-envelope-v0/README.md`
- `fixtures/portfolio-envelope-v0/portfolio-envelope-hygiene-checks.json`
- `fixtures/portfolio-envelope-v0/invalid/*.json`
- `tools/check_portfolio_envelope_contract.py`

as the canonical answer for **what minimal cross-cutting honesty rules should be checked mechanically before the archive treats a shared pack/brief/diff/verify/lineage artifact as fit for further routing, specimen refresh, or assistant reuse**.
