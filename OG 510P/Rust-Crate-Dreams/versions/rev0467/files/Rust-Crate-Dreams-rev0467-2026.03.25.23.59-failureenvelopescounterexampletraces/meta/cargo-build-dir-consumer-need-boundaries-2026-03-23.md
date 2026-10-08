# Cargo build-dir consumer need boundaries — 2026-03-23

This note keeps **P-0489 Cargo Build-Dir Consumer Transition Kit** from collapsing four different claims into one fake “migration advice exists” story.

## Keep these separate

### 1. Observed path scrape is not the same as consumer need
A helper scraping `target/debug/deps` might really need:
- an integration-test binary,
- a final artifact,
- dep-info,
- or only a guessed path to some private intermediate file.

The path shape is evidence.
It is not the need.

### 2. Consumer need is not adapter authority
Even if a helper clearly needs an integration-test binary, that does not by itself say what source authorizes the chosen adapter.
Examples:
- Cargo book docs,
- a release-note / changelog statement,
- an official testing post with a version window,
- an unstable-doc route,
- or only an issue-thread workaround.

### 3. Adapter authority is not windowed viability
A route can be real and still only hold:
- on Cargo 1.94+,
- only on nightly,
- only during dual-layout migration,
- or only with a conservative fallback still preserved.

### 4. Windowed viability is not the overall transition verdict
A matrix row can say a route is `works_with_fallback`.
That still does not settle whether the local migration is safe, dual-support-heavy, or blocked by an upstream gap.

## Working rule

When touching **P-0489**, keep the archive layered as:
1. observed consumer evidence,
2. consumer need,
3. adapter plan,
4. adapter authority,
5. windowed viability,
6. transition verdict / rehearsal bundle,
7. remaining manual-review boundaries.

Do not rephrase all of that as one generic “Cargo layout migration is supported” claim.

## Sources

- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://doc.rust-lang.org/cargo/commands/cargo-build.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
