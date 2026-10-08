# Design: Spec Conformance Pilot Program (`cargo conform pilot`, `conformance-pack/v0`)

## Goal
Make the archive’s spec/conformance work executable as a **ranked rollout plan** instead of a worthy but isolated design.

A serious contribution here is not “write more spec prose”, not “clone compiletest”, and not “ship a certification badge”.
It is a staged program that proves Rust can publish **text identity, vector identity, capability truth, acceptance diffs, and assurance imports** without flattening them.

## Why this needs its own design layer
Current Rust signals make the missing execution order more important:
- Rust now has an official specification trajectory through RFC 3355, the rust-lang-owned FLS, and an upkeep goal;
- 2026 roadmap work makes safety-critical evidence and FLS cadence explicit project concerns;
- the experimental-language-specification goal introduces stability markers and process experiments that need traceable outputs;
- a-mir-formality and std-contract work make executable semantics and programmatic contracts more realistic;
- the archive already has Spec Conformance Kit, Acceptance Surface Kit, and Safety-Critical Evidence Stack, but it still lacked the ranked bridge connecting them.

Sources:
https://rust-lang.github.io/rfcs/3355-rust-spec.html
https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
https://rust-lang.github.io/rust-project-goals/2026/flagships.html
https://rust-lang.github.io/rust-project-goals/2026/experimental-language-specification.html
https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html

## Ranked pilot order

### Pilot 1 — Stable paragraph-linked core-profile lane
Run a narrow, stable conformance profile against ordinary rustc/toolchain lanes.

Must prove:
- `spec-pack/v0` can point at Reference/FLS paragraphs without snapshotting giant books;
- `conformance-vectors/v0` can carry stable vector ids and profile tags;
- `implementation-capabilities/v0` can explain exactly what compiler/runner/target combination ran;
- `conformance-report/v0` can preserve partial coverage without fake universality.

Why first:
- it starts with the most defensible and reusable claim surface;
- it proves the archive can publish paragraph-linked evidence before handling unstable text.

### Pilot 2 — Experimental-language-spec lane
Use the experimental language-specification process as a live test of pre-stable traceability.

Must prove:
- experimental or stability-marked text can be cited without pretending it is already official;
- proposed language text can map to vectors and reports contemporaneously with design work;
- nightly or branch-specific capability declarations stay explicit;
- team/process provenance remains attachable rather than trapped in review threads.

Why second:
- it turns a process experiment into a durable artifact discipline;
- it prevents the archive from treating “draft text exists” as equivalent to stable conformance.

### Pilot 3 — Acceptance-diff lane
Pair conformance reports with compiler-lane acceptance profiles.

Must prove:
- acceptance differences across stable/beta/nightly or solver/borrow-check lanes remain explicit;
- implementation quirks, workarounds, and partial support do not get mislabeled as conformance failures;
- one review can compare “spec expectation” and “accepted today” without collapsing them;
- future compiler changes can produce archaeology-friendly diff reports.

Why third:
- it is where spec dreams meet compiler reality;
- it makes the broader stack more honest for real users.

### Pilot 4 — Unsafe-contract / safety-doc lane
Use normative-unsafe and safety-contract work as a first safety-oriented consumer.

Must prove:
- safety-critical evidence can import a conformance subject rather than restating language semantics ad hoc;
- unsafe-pattern documentation and std-contract work can attach to the same traceability culture;
- authoritative docs, local rationale, and proof/runtime-checking assumptions remain separate;
- partial or underdocumented patterns can remain first-class `INCONCLUSIVE` or out-of-scope outcomes.

Why fourth:
- it converts the stack from language-tooling infrastructure into assurance infrastructure;
- it matches one of the clearest 2026 Rust roadmaps.

### Pilot 5 — Release / qualification / archaeology lane
Attach the resulting packs to a real release-candidate or qualification-style review bundle.

Must prove:
- spec version, FLS cadence, capability profile, vectors, and outcomes can survive as attachable artifacts;
- conformance diffs over time are readable months later;
- release/policy/audit consumers can import the same packs without large raw test logs;
- the stack still works when coverage is partial and claims are narrow.

Why fifth:
- it is strategically important, but only after the lower layers are honest and reusable;
- it tests whether the archive’s “tight, durable evidence” posture survives contact with long-lived consumers.

## Shared schema discipline
Every pilot must keep these truths separate:
1. **stable text** vs **experimental text**
2. **normative prose** vs **executable vectors**
3. **conformance result** vs **acceptance diff**
4. **implementation capability** vs **policy conclusion**
5. **assurance import** vs **language-semantic source**
6. **portable summary** vs **large raw attachments**

## Immediate archive consequences
Read this together with:
- [`design/conformance-traceability-stack.md`](./conformance-traceability-stack.md)
- [`design/spec-conformance-kit.md`](./spec-conformance-kit.md)
- [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md)
- [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md)
- [`proposals/epic-spec-conformance-kit.md`](../proposals/epic-spec-conformance-kit.md)

The archive should now treat **Spec Conformance Kit** less like an isolated language-tooling idea and more like the execution substrate for a broader conformance-traceability story.
