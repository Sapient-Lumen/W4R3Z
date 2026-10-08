---
id: P-0524
title: Crate Example Surface Pack Kit — official quickstarts, prerequisite receipts, success witnesses, and example-surface diffs for library authors
status: idea
domains: [crates, dx, documentation, examples, onboarding, quickstarts, docsrs, supportiveness]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://rust-lang.github.io/api-guidelines/documentation.html
  - https://doc.rust-lang.org/cargo/reference/cargo-targets.html
  - https://doc.rust-lang.org/cargo/commands/cargo-doc.html
  - https://doc.rust-lang.org/cargo/reference/features.html
  - https://doc.rust-lang.org/rustdoc/scraped-examples.html
  - https://doc.rust-lang.org/rustdoc/documentation-tests.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://docs.rs/about/metadata
  - https://docs.rs/about/builds
  - https://docs.rs/trycmd/latest/trycmd/
  - https://docs.rs/term-transcript/latest/term_transcript/
  - https://docs.rs/crate/mdbook/latest
  - https://docs.rs/crate/cargo-generate/latest
---

# Problem

The archive now has much stronger receiver-facing lanes for choosing crates, understanding support claims, fitting interop profiles, getting compile-time guidance, handling runtime failure handoff, upgrading, leaving a crate, choosing setup scenarios, reasoning about performance posture, understanding observability surfaces, reviewing authority / determinism posture, reviewing lifecycle / shutdown behavior, reviewing resource / saturation posture, reviewing persistence / durability posture, and reviewing downstream test support.

It still needs a sharper answer to a different but equally ordinary downstream question:

> “If I adopt this crate, what is the smallest officially supported path from zero to first success, what exactly does it require, and what evidence proves that path still works?”

That gap matters because Rust’s example substrate is real but fragmented.

The December 2025 Rust vision-doc work explicitly recommends more supportive interfaces from crates.
The 2025 State of Rust survey says online documentation remains the preferred canonical reference and studying the code remains the next most important learning surface.
The API Guidelines warn that example code is often copied verbatim by users.
Cargo gives crates first-class `examples/` targets and compiles them under `cargo test` by default to protect them from bit-rot.
Rustdoc scraped examples can link `examples/` code back into docs, but remain unstable.
Docs.rs lets crates customize metadata while also imposing a sandbox with blocked network access and mostly read-only sources.
And tools like `trycmd`, `trybuild`, `skeptic`, `term-transcript`, `mdBook`, and `cargo-generate` cover important slices of example testing, transcript rendering, tutorial publishing, and template bootstrapping.

But that substrate still does **not** give maintainers one boring review object for questions like:

- which example is the *official quickstart* versus merely illustrative,
- where a prerequisite came from (README prose, docs.rs metadata, a guide, an adapter test, or maintainer judgment),
- what *counts* as success for a quickstart,
- whether success was actually witnessed or merely inferred,
- whether each major adoption scenario has any official path at all,
- whether the “official” quickstart silently moved behind a feature flag, service dependency, credential, browser, board, or guide,
- and how that first-success surface changed across releases.

The worthy crate is therefore **not** another docs portal, **not** another tutorial CMS, **not** another generic snapshot harness, **not** another template generator, and **not** just scraped examples but nicer.
It is a **Crate Example Surface Pack Kit**: a crate that helps maintainers author, verify, diff, and export the receiver-facing quickstart / first-success support contract their crate gives other people.

After re-reading the current Cargo / rustdoc / docs.rs surface, the sharpest missing layer is now even more specific: the crate should make **official-start authority**, **entrypoint viability**, and **hosted visibility** reviewable instead of leaving them implicit inside prose, examples folders, or hosted docs defaults.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What officially supported example paths exist for this crate?**
2. **Which one is the smallest supported quickstart for each adoption scenario?**
3. **What prerequisites does each path rely on, and where did that prerequisite knowledge come from?**
4. **What counts as success for each path, and was that success actually witnessed?**
5. **How do README snippets, rustdoc examples, `examples/` targets, guides, and docs.rs surfaces link together?**
6. **Which paths are stable support contracts versus best-effort demos or manual-review-only starts?**
7. **How did that example-support surface change across releases?**

That is more valuable than leaving users to reconstruct onboarding guidance from README prose, examples folders, issue comments, guides, blog posts, and cargo commands copied from memory.

# What it provides

- `example-surface-pack.toml` — versioned declaration of supported example families, support levels, environment classes, success signals, prerequisite origins, and doc linkages.
- `example-catalog.receipt.json` — observed receipt for example sources found in README, rustdoc, `examples/`, guides, or external docs.
- `quickstart-path.manifest.json` — named official paths such as `hello_path`, `authenticated_request`, `local_persistence`, `stream_processing`, `ffi_embedding`, `no_std_bootstrap`, or `manual_review_required`.
- `quickstart-authority.receipt.json` — explicit receipt for what source actually blesses a path as the official receiver-facing start.
- `adoption-scenario.manifest.json` — scenario-specific grouping of official quickstarts and reference examples.
- `example-environment.report.json` — explicit classification such as `pure_local`, `temp_files_only`, `network_loopback`, `external_network`, `credentialed_service`, `board_or_device`, `browser_host`, or `manual_review_required`.
- `prerequisite-origin.receipt.json` — explicit provenance for each prerequisite, such as `cargo_manifest`, `package_metadata_docsrs`, `readme_text`, `guide_text`, `adapter_fixture`, `ci_observation`, or `maintainer_assertion`.
- `success-witness.receipt.json` — explicit record of what success evidence was actually observed, such as normalized stdout, a generated file, an HTTP response, compile success, or a manual-review boundary.
- `scenario-coverage.report.json` — whether each adoption scenario has a declared official quickstart, only reference examples, or no honest first-success path yet.
- `docs-example-linkage.report.json` — checks whether README sections, rustdoc items, guides, and `examples/` targets still point at each other coherently.
- `entrypoint-viability.matrix.json` — matrix joining entrypoint kind, command family, feature/env lane, and result such as `viable`, `visible_only`, `skipped_required_features`, or `manual_review_required`.
- `visibility-surface.report.json` — explains what rustdoc/docs.rs surfaces are visible, under what metadata/targets/features/scrape mode, and what that visibility does **not** prove about local runnable success.
- `example-output.report.json` — records whether success is a `stdout_snapshot`, `stderr_snapshot`, `returned_value`, `generated_file`, `http_exchange`, `rendered_doc_example`, or `manual_review_required`.
- `example-support-check.report.json` — verifies that declared example paths still build, still satisfy their environment rules, still match their support-level claims, and still have success witnesses that fit the declared path.
- `example-normalization.profile.json` — explicit placeholders/redaction rules for dynamic output such as temp paths, dynamic ports, timestamps, UUIDs, or secret-shaped values.
- `example-surface-diff.report.json` — compares two releases and classifies `quickstart_added`, `quickstart_removed`, `prerequisite_changed`, `success_witness_changed`, `scenario_coverage_changed`, `docs_linkage_changed`, `example_output_changed`, `support_level_changed`, and `manual_review_required`.
- `example-summary.md` — short human-facing explanation of where a user should start, what prerequisites are required, what success looks like, and which examples are officially supported.
- `cargo example-surface check` — verify quickstarts, linkage, prerequisite provenance, success witnesses, and support claims.
- `cargo example-surface doctor` — explain why a declared quickstart is not trustworthy enough yet (missing witness, hidden prerequisite, stale docs linkage, or no official path for a scenario).
- `cargo example-surface diff <old> <new>` — show how official examples changed.
- `cargo example-surface summary` — render a concise onboarding guide.

# What the crate should provide other people

1. **Official quickstarts** above README folklore and demo sprawl.
2. **Prerequisite honesty** so users know whether a path depends on features, metadata, credentials, a running service, a board, a browser, or only local files.
3. **Success witnesses** so “it worked” becomes reviewable rather than implied.
4. **Scenario coverage truth** so a crate can honestly say which adoption shapes actually have an official first-success path.
5. **Authority honesty** so downstream users can see *why* one path counts as the official start instead of inferred prominence.
6. **Entrypoint viability truth** so README snippets, rustdoc examples, guide commands, and `examples/` targets do not get flattened into one fake “works” claim.
7. **Hosted visibility honesty** so docs.rs and rustdoc appearance does not masquerade as local runnable proof.
8. **Docs / example linkage** so README snippets, rustdoc examples, and `examples/` targets stop drifting silently apart.
9. **A diffable example surface** so release reviewers can spot when the only good getting-started path disappeared or got harder.
10. **Importable vocabulary** for docs portals, crate selectors, supportiveness packs, and release review bots.
11. **A support-level taxonomy** so maintainers can say which paths are official quickstarts, official reference examples, best-effort demos, docs-only examples, or manual-review-only cases.

# Persona / who it’s for

- library authors whose users repeatedly ask “which example should I start with?”
- SDK/client maintainers who should publish one clear local/loopback happy path and one clearly demoted credentialed path
- CLI/tool maintainers who want README command snippets, examples, and output witnesses to stay aligned
- embedded / `no_std` / WASM / browser / FFI maintainers who need explicit environment honesty and scenario coverage truth
- downstream teams trying to choose the smallest trustworthy adoption path for a new crate
- docs/tool authors who want stable example metadata instead of scraping prose heuristically

# Users & user stories

- **Parser crate maintainer**: “Publish one official ‘parse one string, inspect one AST’ quickstart and tell users which examples are deeper reference material only.”
- **HTTP SDK maintainer**: “Declare the unauthenticated loopback quickstart, the credentialed real-service path, and which of those actually has a witnessed success receipt.”
- **CLI maintainer**: “Keep README commands, `examples/`, and normalized stdout/stderr success witnesses in sync so installation and first use stay boring.”
- **Embedded maintainer**: “Say whether the first supported path is board-only, host-simulated, or manual-review-only, and what toolchain / flashing assumptions it makes.”
- **Proc-macro maintainer**: “Publish the smallest compile-success example, the linked compile-fail companions, and the success witness for the starter path.”
- **Downstream integrator**: “Diff two releases and see whether the official quickstart moved behind a new feature, credential, board, or service.”

# Prior art (and why it’s insufficient)

- Rust API Guidelines already explain how examples should be written and why users copy them.
- Cargo already has first-class `examples/` targets and compiles them by default with `cargo test`.
- Rustdoc can test documentation examples and has an unstable scraped-examples path for linking `examples/` code back into docs.
- Docs.rs already has metadata controls and a specific sandboxed build environment.
- `trycmd` supports CLI-oriented executable example testing.
- `term-transcript` supports transcript rendering and parsing.
- `mdBook` supports tutorial/book publishing.
- `cargo-generate` supports project templating.

Those tools are real and useful. They just do not publish one joined, reviewable contract that tells another human:

- which start is *official*,
- what it *really* requires,
- what success *looked like* when last checked,
- whether that success was *witnessed* or only inferred,
- and whether each important adoption scenario has a trustworthy path.

# Design principles

1. **First success over total example coverage.** Prioritize the smallest honest path per scenario.
2. **Conservative provenance over synthesis.** Unknown prerequisite origin should stay unknown.
3. **Witness, do not imply.** Success claims need receipts or explicit manual-review boundaries.
4. **Scenario honesty over green demos.** A crate may have many examples and still lack an official path for an important adoption shape.
5. **Small receipts over giant sites.** Reviewable artifacts beat sprawling generated documentation.
6. **Adapters over replacements.** Import from `trycmd`, rustdoc, docs.rs metadata, or guide tooling where helpful.
7. **Release diffs matter.** Losing or weakening a first-success path is support drift.

# Why this still looks worth building

The adjacent tools are real, which is exactly why this proposal now looks sharper rather than weaker.
The survey says docs and code are where people learn.
The API Guidelines say users copy examples.
Cargo and rustdoc already keep examples tied to the codebase.
Docs.rs already exposes metadata and build constraints.
And today’s example/test/tutorial tools already cover slices of the workflow.

That combination strengthens the case that the missing value is the **crate-authored quickstart/support contract above them**, not another attempt to replace them.


# Implementation-ready shape now

The archive now has enough evidence and enough fixture vocabulary to stop treating **P-0524** as just a good idea.

A believable `0.1` should now ship around seven review objects:

1. **quickstart path** — the smallest official path per scenario,
2. **environment class** — whether that path is pure-local, loopback, credentialed, board/device, browser, or manual-review-only,
3. **prerequisite origin** — where the setup knowledge came from,
4. **success witness** — what counted as proof of life and whether it was observed,
5. **docs/example linkage** — whether README, rustdoc, guides, and `examples/` still agree,
6. **scenario coverage** — which adoption shapes have an honest official path,
7. **normalization boundary** — what dynamic output can be normalized without hiding real contract drift.

That is why the crate should be planned as a **joined support contract** rather than as a tutorial engine, snapshot tool, or templating system.
