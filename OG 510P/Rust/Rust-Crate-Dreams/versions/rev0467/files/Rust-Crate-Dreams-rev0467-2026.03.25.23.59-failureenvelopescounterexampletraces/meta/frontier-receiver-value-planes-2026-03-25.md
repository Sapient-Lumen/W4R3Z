# Frontier receiver value planes — 2026-03-25

This note answers a sharper planning question:

**What should each leading lane provide other people in practice?**

The test here is receiver-first.
If another team cannot say what job got easier, what file they receive, and what the crate refuses to claim, the lane is still underplanned.

## P-0509 — Crate Ecosystem Pathfinder & Decision-Pack Kit

### Receiver
- team choosing among 2–8 plausible crates for one concrete job

### What it should provide
- a repeatable comparison packet
- elimination logic
- preserved basis and rationale
- a final decision packet another reviewer can reopen without redoing the whole search

### `0.1` artifact family
- `task-profile.json`
- `candidate-import.json`
- `decision-pack.json`
- `starter-set.lock`

### CLI shape
- `cargo pathfinder compare`
- `cargo pathfinder decide`

### Library seam
- task ingestion, candidate import, scoring/exclusion, packet rendering

### Refusal boundary
- not “the best crate for everyone”; only best-under-stated-task-and-basis

## P-0536 — Crate Knowledge Pack Kit

### Receiver
- reviewer or later maintainer trying to replay why the earlier packet was believable

### What it should provide
- pinned citations
- machine-usable support bundle
- hosted/local/doc/build caveat preservation
- frozen import basis for later rechecks

### `0.1` artifact family
- `basis-lock.json`
- `review-packet.json`
- `citation-locator.json`
- `build-surface.json`

### CLI shape
- `cargo knowledge-pack lock`
- `cargo knowledge-pack render`

### Library seam
- source normalization, locator generation, lock persistence, report rendering

### Refusal boundary
- not a perfect mirror of the internet or every build condition ever

## P-0472 — Docs.rs Build Parity & Evidence Kit

### Receiver
- maintainer or evaluator who needs to know what docs.rs actually proved and what it did not

### What it should provide
- hosted-doc preflight
- hosted-vs-local diffs
- target/build metadata interpretation
- issue bundles for actionable parity gaps

### `0.1` artifact family
- `docsrs-preflight.json`
- `hosted-local-diff.json`
- `build-metadata.import.json`
- `parity-issue-bundle.json`

### CLI shape
- `cargo docsrs-preflight`
- `cargo docsrs-diff`

### Library seam
- metadata import, docs.rs route parsing, diff classification, report rendering

### Refusal boundary
- not a new docs host and not a stable promise that rustdoc HTML is a stable API

## P-0484 — Toolchain & Target Support Contract Kit

### Receiver
- team shipping to a constrained or unusual target that needs explicit support truth

### What it should provide
- supported target tuple list
- component availability
- tier/import caveats
- target-specific support ceiling

### `0.1` artifact family
- `target-support.report.json`
- `component-availability.report.json`
- `toolchain-ceiling.note.md`

### CLI shape
- `cargo target-support`
- `cargo component-availability`

### Library seam
- target tuple import, rustup/component interpretation, policy rendering

### Refusal boundary
- not certification and not proof that user code works on every imported target

## P-0535 — Dependency Lifecycle Transition Kit

### Receiver
- maintainer revisiting a previously accepted dependency under new evidence

### What it should provide
- recheck intake
- changed-since-last-answer summary
- transition/off-ramp plan
- successor or downgrade packet

### `0.1` artifact family
- `trigger-intake.receipt.json`
- `decision-revalidation.report.json`
- `transition-plan.json`
- `successor-note.md`

### CLI shape
- `cargo dep-transition intake`
- `cargo dep-transition revalidate`
- `cargo dep-transition plan`

### Library seam
- signal intake, basis lookup, diff classification, transition rendering

### Refusal boundary
- not autonomous dependency management and not a silent upgrader

## P-0496 — Cargo Vendor & Source Parity Kit

### Receiver
- enterprise/offline/restricted-delivery operator who must know whether the public and mirrored routes still mean the same thing

### What it should provide
- source-parity report
- mirror-readiness report
- degraded-mode caveats
- alternate-registry risk notes

### `0.1` artifact family
- `source-parity.report.json`
- `mirror-readiness.report.json`
- `degradation-note.md`

### CLI shape
- `cargo source-parity`
- `cargo mirror-readiness`

### Library seam
- source graph import, replacement interpretation, parity rendering

### Refusal boundary
- not full provenance attestation and not a registry implementation

## P-0431 — Public Dependency Boundary Kit

### Receiver
- maintainer or reviewer who needs to know what dependencies became part of the public promise

### What it should provide
- public/private exposure report
- semver-relevant boundary drift
- witness-backed boundary explanations

### `0.1` artifact family
- `public-boundary.report.json`
- `boundary-delta.report.json`
- `witness-program.note.md`

### CLI shape
- `cargo public-boundary`
- `cargo public-boundary diff`

### Library seam
- rustdoc JSON import, semver import, boundary classification

### Refusal boundary
- not complete semver judgment in isolation from real type/public API evidence

## P-0486 — Debuggability Support Contract Kit

### Receiver
- engineer or support team that must know what debugging support the release actually carries

### What it should provide
- debugger/OS/version matrix
- symbol/visualizer sidecar presence
- async/debug caveats
- explicit unsupported paths

### `0.1` artifact family
- `debug-support.report.json`
- `symbol-sidecar.report.json`
- `unsupported-paths.note.md`

### CLI shape
- `cargo debug-support`
- `cargo debug-sidecars`

### Library seam
- target/debugger matrix import, sidecar inspection, support rendering

### Refusal boundary
- not guaranteed debugger quality and not a replacement for debugger vendors or rustc itself

## P-0537 — Compile Iteration Feedback Kit

### Receiver
- developer or build engineer trying to explain rebuilds and iteration cost

### What it should provide
- why-rebuilt explanation
- build hot spots
- actionable, bounded suggestions

### Refusal boundary
- not a general performance oracle and not a promise to fix Cargo internals

## P-0538 — Concurrency Contract Kit

### Receiver
- engineer choosing among concurrency surfaces and needing honest semantic comparison

### What it should provide
- comparable contracts for ordering, cancellation, closure, fairness, visibility, and error semantics

### Refusal boundary
- not proof of whole-program concurrency correctness

## Takeaway

The strongest frontier lanes are the ones where the receiver, files, imports, and refusal boundary are all concrete enough that a `0.1` could actually be piloted.
