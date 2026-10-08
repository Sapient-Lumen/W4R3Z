# Gap: specification traceability and executable conformance

## What is missing
Rust’s specification work is finally real enough to build on, but the ecosystem still lacks a boring way to turn specification progress into executable, portable conformance evidence.

The upstream signals are stronger than they used to be:
- RFC 3355 says Rust needs an accurate specification to serve unsafe-code authors, safety-critical users, language designers, and tooling maintainers.
- The accepted 2025H1 goal moved the Ferrocene Language Specification (FLS) into rust-lang infrastructure and published it under the Rust Project.
- The proposed 2025H2 follow-on goal is explicitly about building the capability and capacity to keep the FLS up to date.
- Rust’s 2026 flagship themes now list **stabilizing FLS release cadence** as a Safety-Critical Rust milestone.

Sources:
- https://rust-lang.github.io/rfcs/3355-rust-spec.html
- https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
- https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## The current seam is still awkward
The new FLS is already a serious document, with paragraph identifiers, normative sections, a changelog, and explicit “conforming tool” language. But its own scope note says it is **not intended as a document enabling conformance between compilers**.

That is the opening for an ecosystem contribution.

Today we have pieces, but not a shared boundary:
- the spec text itself;
- compiler-internal test infrastructure like `compiletest`;
- reusable diagnostic test runners like `ui_test`;
- format-specific conformance patterns like `toml-test-rs`;
- bespoke corporate or qualification pipelines.

What is still missing is the connective tissue:
- how to pin the normative text or paragraph set used for a given run;
- how to declare which targets / editions / features / libraries are in scope;
- how to map `spec_ref -> test vector -> result` in a machine-readable way;
- how to publish partial coverage honestly instead of implying universal conformance.

Sources:
- https://rust-lang.github.io/fls/general.html
- https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
- https://docs.rs/ui_test
- https://github.com/toml-rs/toml-test-rs

## Why this matters
Without a shared conformance substrate, Rust’s growing specification work risks helping humans more than tools.
That would still be useful, but it would leave several high-leverage use cases unnecessarily bespoke:
1. **Safety-critical and qualified toolchains** need traceable evidence, not just prose.
2. **Compiler and toolchain teams** need a portable way to run targeted semantic regressions and archive results.
3. **Alternative implementations / analyzers / transpilers** need partial, profile-based conformance claims rather than all-or-nothing marketing.
4. **Library and platform teams** need small executable profiles for language subsets (`core`, `alloc`, `no_std`, FFI-heavy, unsafe-heavy, target-specific lanes).

The FLS maintenance goal itself says active and passive beneficiaries include tool vendors, library vendors, and integrators, which is a strong hint that the missing next layer is broader than one compiler’s internal test suite.

Source:
- https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html

## What “good” looks like
A worthy ecosystem contribution here is **not** “write the Rust specification” and **not** “replace compiletest”.
It is a thinner and more durable substrate:
- one `spec-pack/v0` that points at the normative sources and the exact paragraph ids / digests in scope;
- one `conformance-vectors/v0` for executable tests and fixtures;
- one `implementation-capabilities/v0` that declares what a runner/toolchain actually supports;
- one `conformance-report/v0` that records results, exclusions, and traceability;
- and one `conformance-pack/v0` bundle that can be attached to CI, releases, or qualification evidence.

That would let the ecosystem turn “we have a spec document” into “we can run a scoped, replayable, reviewable conformance story”.
