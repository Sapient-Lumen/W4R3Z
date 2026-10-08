# Cargo build-dir consumer frontier — consumer need, adapter authority, and windowed rehearsal truth (2026-03-23)

This note deepens **P-0489 Cargo Build-Dir Consumer Transition Kit** around one sharper question:

> When a build-dir-coupled helper breaks, what was it really trying to do, what source authorizes the suggested fix, and in which Cargo/layout window does that fix honestly hold?

## Main judgment

The archive already had a solid answer for:
- **who is touching Cargo internals** (`consumer-inventory.manifest.json`),
- **what risky path assumptions were observed** (`consumer-audit.report.json`),
- **what safer route might exist** (`path-contract.json` / `adapter-plan.json`),
- and **whether that route is broadly viable** (`adapter-viability.report.json`).

What it still left too easy to flatten was the difference between:
1. a helper scraping a path because it wants an integration-test binary,
2. a helper scraping a path because it wants build-script-owned output,
3. a helper scraping a path because it wants a final artifact,
4. a workaround that is clearly documented in Cargo,
5. a workaround named only in a version-windowed testing post,
6. and a workaround that is still really just a heuristic or upstream gap.

That gap matters more now because Cargo’s March 2026 build-dir testing post is unusually concrete:
- it says the build-dir layout is internal-only while acknowledging that many projects still rely on unspecified details because features are missing;
- it asks people to test not just builds but release processes and anything else touching build-dir / target-dir under `-Zbuild-dir-new-layout`;
- it names concrete failure modes and even gives one version-windowed migration hint (`std::env::var_os("CARGO_BIN_EXE_*")` for Cargo 1.94+);
- while the build-cache docs keep final-vs-intermediate artifact boundaries explicit and external-tools docs keep JSON coverage limited to Cargo / rustc output.

So the sharper missing crate contribution is not just “build-dir migration help”.
It is a compact support contract for:
- **consumer need truth**,
- **adapter authority truth**,
- **windowed viability truth**,
- and **rehearsal-bundle truth**.

## Review objects to promote now

### 1. `consumer-need.report.json`
Purpose: say what job the consumer was actually trying to do instead of just preserving the scraped path shape.

Suggested classes:
- `integration_test_binary`
- `build_script_owned_output`
- `final_artifact`
- `user_requested_artifact`
- `dep_info`
- `workspace_topology_guess`
- `manual_review_required`

### 2. `adapter-authority.receipt.json`
Purpose: say what source class actually justifies the adapter claim.

Suggested classes:
- `cargo_book`
- `release_notes`
- `official_call_for_testing`
- `unstable_docs`
- `project_goal`
- `issue_thread_only`
- `local_heuristic`
- `manual_review_required`

### 3. `windowed-viability.matrix.json`
Purpose: record whether a route holds across stable/nightly, Cargo-version floors, legacy/new-layout rehearsal, and fallback pressure.

Suggested row verdicts:
- `works_as_documented`
- `works_with_fallback`
- `nightly_only`
- `blocked_on_upstream`
- `manual_review_required`

### 4. `rehearsal-support-bundle.manifest.json`
Purpose: portable inventory joining need, authority, viability, inventory, audit, and transition artifacts for migration rehearsal.

## What a worthy crate should provide other people after this pass

1. **Need honesty** — “the tool scraped `target/debug/deps`” should not be the highest-level summary if the real need was “find the integration-test binary”.
2. **Authority honesty** — a blog/testing workaround should not silently become “stable Cargo API”.
3. **Window honesty** — a fix that works in Cargo 1.94+ or nightly rehearsal should not silently become timeless stable advice.
4. **Portable rehearsalability** — another maintainer should be able to diff legacy layout, custom `build.build-dir`, and new-layout rehearsal bundles without re-reading issue threads.

## Sources

- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://doc.rust-lang.org/cargo/commands/cargo-build.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
