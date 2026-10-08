# Native-build stack — implementation queue refresh (2026-03-23)

This note revisits the native-build stack with newer Rust/Cargo/docs.rs signals and asks a narrower question:

> What should this stack look like in theory and in practice if we actually wanted to build it now?

The stack still has three parts:

1. **P-0046 Buildscript UX Kit**
2. **P-0059 Buildscript Testkit**
3. **P-0058 Native Deps Kit**

## Main judgment

The order still matters.
But the stack is now more relevant to the practical repo queue than it looked on 2026-03-08.

### Why it matters more now

#### 1. Build and support truth are still central pain

The 2025 State of Rust survey still says resource usage remains near the top of real-world problems, and online documentation remains the preferred canonical learning source. That means crates that make build behavior more legible and supportable now matter beyond niche `-sys` maintainers.

#### 2. Cargo is actively moving the ground under tooling

Cargo is asking the ecosystem to test `-Zbuild-dir-new-layout` because many tools and processes still rely on internal layout details. That is exactly the kind of ecosystem moment when explanation and migration bundles become more valuable than one-off patches.

#### 3. Docs.rs makes build assumptions visible

Docs.rs now documents a concrete sandbox: nightly compiler, read-only source trees, no network access, explicit RAM/time/log/target limits, and a recommendation to test with `cargo docs-rs` while acknowledging it is not a perfect replica. That means build and native-dependency crates can no longer be planned as if local builds were the only support surface.

#### 4. Native dependency declaration exists, but support bundles do not

`system-deps` already demonstrates declarative dependency metadata and `vcpkg` already demonstrates Windows/MSVC-oriented discovery and metadata emission. But downstream users still do not get one standard reviewable answer about vendored/system choice, package-manager assumptions, backend attempts, ABI expectations, or override handoff.

#### 5. Safety-critical and mixed-language adoption raise the bar

The 2026 safety-critical write-up says the ecosystem thins out quickly at higher criticality, and explicitly calls interop and long-lived FFI boundaries part of the safety story. That strengthens the case for native-build crates that preserve receipts rather than hiding behavior in ad hoc `build.rs` code.

## Recommended implementation sequence now

### First — P-0046 Buildscript UX Kit

This should still go first because every other lane benefits from a stable explanation vocabulary.

**What it should provide other people:**
- a small support bundle for failed or suspicious build-script runs,
- a short human summary,
- a typed machine-readable report,
- and policy gates that let CI reject known-bad warning/failure classes.

**Why first in practice:**
- Cargo still reruns build scripts conservatively by default unless authors emit `rerun-if-*` instructions.
- Build issues are often diagnosed from raw logs and folklore.
- A support bundle helps both pure-Rust build issues and native-dependency issues.

### Second — P-0059 Buildscript Testkit

This should still go second because drift-testing is easier once report vocabulary is stable.

**What it should provide other people:**
- deterministic fixture runs,
- normalized directives and observed environment inputs,
- and golden comparisons that show whether build behavior changed meaningfully.

**Why second in practice:**
- it lets maintainers stop diffing raw logs,
- gives CI a credible regression story,
- and creates the proving ground that P-0058 will need.

### Third — P-0058 Native Deps Kit

This should remain the third layer, but it is now more urgent than before.

**What it should provide other people:**
- a declared native contract,
- backend attempt receipts,
- package-manager and vendoring mode truth,
- ABI/provenance hints,
- and a doctor report for the current machine or CI environment.

**Why third in practice:**
- it spans more backend complexity than P-0046/P-0059,
- but the ecosystem pressure for it is higher now,
- and it becomes much stronger if it can reuse the explanation and fixture vocabulary already established below it.

## Shared theory of the stack

The stack is strongest when each layer has a different handoff object.

### P-0046 — support bundle layer

Answers:
- what happened,
- what mattered,
- what should I try next.

### P-0059 — drift-test layer

Answers:
- did the script still emit what we expected,
- what changed,
- and is that change acceptable.

### P-0058 — native-contract layer

Answers:
- what native support was promised,
- what backend path actually ran,
- what this machine or CI image is missing,
- and what override/vendoring/system route is in effect.

## Suggested `0.1` artifact map

### P-0046
- `buildscript-report.json`
- `buildscript-summary.txt`
- `policy-gate.report.json`
- `support-snapshot.redacted.txt`

### P-0059
- `fixture-manifest.toml`
- `buildscript-run.report.json`
- `directives.normalized.json`
- `env-observation.receipt.json`

### P-0058
- `native-contract.toml`
- `native-resolution.report.json`
- `backend-attempts.receipt.json`
- `resolution-mode.lock.json`
- `abi-provenance.report.json`
- `consumer-doctor.txt`

## What would make this stack worthy

This stack becomes a worthy contribution if it lets a maintainer hand another human or tool a compact bundle instead of saying:

- “re-run with `-vv` and paste the whole thing,”
- “it works on my machine,”
- “set some env vars until it links,”
- or “we vendor sometimes, I think.”

That is the quality bar.

## What would make it drift again

Avoid these failure modes:

- turning P-0058 into a universal package manager,
- turning P-0059 into a Cargo emulator,
- turning P-0046 into a log prettifier without typed semantics,
- or collapsing all three into one vague “native build toolkit”.

## Sources

- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ (“Why is Cargo rebuilding my code?”) — https://doc.rust-lang.org/cargo/faq.html
- Cargo release notes (`OUT_DIR` build-time behavior change) — https://doc.rust-lang.org/beta/releases.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs about page — https://docs.rs/about
- What does it take to ship Rust in safety-critical? — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- system-deps docs — https://docs.rs/system-deps/latest/system_deps/
- `system-deps` standardization discussion — https://github.com/gdesmott/system-deps/issues/97
- vcpkg docs — https://docs.rs/vcpkg/latest/vcpkg/
