## Execution addendum (rev0420)
This epic should now be read together with `design/package-intake-gateway-execution-blueprint-2026Q1.md`.

Interpretation rule:
- this proposal still answers **why the seam is worth funding**;
- the execution blueprint now answers **what a serious v0 should actually ship**;
- and the project should stay a **portable package-ingress review layer**, not a registry clone, malware-score empire, installer monopoly, or sandbox substitute.

# Epic Proposal: Package Intake Gateway (`cargo intake` + `package-intake-pack/v0`)

## Why this is worthy
Rust still lacks one honest boundary between **package publication** and **local build / install mutation**.

That gap stopped looking theoretical in March 2026:
- the Cargo security advisory says a vulnerability in the `tar` crate used by Cargo to extract packages during a build can let a malicious crate change permissions on arbitrary directories;
- the same advisory tells users of alternate registries to verify impact with their vendor, which is a blunt reminder that route semantics matter;
- `cargo package` already has real payload semantics (normalized manifest, lockfile inclusion, flattened symlinks, pristine extraction/build verification), but those facts are not exported as one portable intake story;
- `cargo install` still differs materially in lockfile and config-discovery semantics;
- crates.io is publishing better trust and freshness signals (`pubtime`, Trusted Publishing controls), while the malware-notification policy now pushes routine removals toward RustSec advisories rather than ambient blog watching;
- and sandboxed build scripts only start **after** package ingress, not at the ingress boundary itself.

Sources:
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://doc.rust-lang.org/cargo/commands/cargo-install.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

## Proposal
Define a thin **Package Intake Gateway** with:
- a companion CLI, `cargo intake`;
- a portable bundle, `package-intake-pack/v0`;
- core artifacts:
  - `intake-subject/v0`
  - `intake-route-report/v0`
  - `intake-payload-report/v0`
  - `intake-staging-receipt/v0`
  - `intake-decision-brief/v0`
  - `intake-handoff/v0`
- imported references to adjacent layers rather than reimplementation:
  - package-admission artifacts,
  - dependency-review artifacts,
  - compile-time/build authority artifacts,
  - consumer-install artifacts,
  - incident / trust / route evidence where relevant.

## What it should prove
A serious v0 should prove that Rust teams can carry these truths together without flattening them:
1. **route identity** — crates.io, alternate registry, exact-copy mirror, vendored directory, local registry, git/path, or direct tarball;
2. **payload identity** — which normalized package payload was staged;
3. **staging/extraction truth** — where and how it was unpacked or verified;
4. **lock/resolution truth** — packaged lock used, ignored, regenerated, unavailable, or offline-constrained;
5. **handoff truth** — what later still belongs to dependency review, build execution, consumer install, or incident response.

## Recommended implementation order
1. crates.io dependency/package-verify lane
2. alternate-registry and source-replacement lane
3. `cargo install` source-build lane
4. offline vendor/local-registry lane
5. incident-response / replay lane

## Non-goals
- a registry replacement;
- a universal malware score;
- a new installer monopoly;
- a stealth reimplementation of Cargo package fetch/install;
- or a generic archive-extraction utility pretending to be ecosystem strategy.

## Success criteria
This epic is successful when a later reviewer can answer:
- what route produced the local package intake,
- what payload was under review,
- what extraction/staging guard posture applied,
- what lock/resolution assumptions held,
- and which later layers still have to run,

without reconstructing that story from temp directories, logs, and memory.

## Read this with
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-2026Q1.md`
- `gaps/package-intake-extraction-route-quarantine-and-handoff-truth.md`
- `design/package-admission-stack.md`
- `design/dependency-review-stack.md`
- `design/consumer-install-kit.md`
- `design/distribution-route-mobility-stack.md`
