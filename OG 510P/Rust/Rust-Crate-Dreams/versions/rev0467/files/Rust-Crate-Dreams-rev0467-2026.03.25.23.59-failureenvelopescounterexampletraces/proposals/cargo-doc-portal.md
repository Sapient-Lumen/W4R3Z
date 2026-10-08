---
id: P-0049
title: cargo-doc-portal — local docs.rs-like portal for workspace + dependency docs
status: idea
domains: [cargo, docs, tooling, ux]
last_reviewed: 2026-03-01
evidence:
  - https://users.rust-lang.org/t/cargo-doc-open-doesnt-show-dependency-documentation/134481
  - https://github.com/rust-lang/cargo/issues/3805
  - https://github.com/rust-lang/cargo/issues/8104
  - https://users.rust-lang.org/t/homepage-for-the-documentation-of-a-workspace/46258
---

# Problem
`cargo doc` happily renders documentation for a whole dependency tree, but **`cargo doc --open` drops you on a single crate page** with no “portal” experience: no workspace landing page, weak navigation to dependency docs, and no seamless offline linkage to `std`. This is a recurring friction point for “browse docs locally” workflows.

# Users & user stories
- Library dev: “I want a **docs.rs-like landing page** locally so I can browse my workspace and dependencies without guessing URLs.”
- Reviewer: “I’m auditing a dependency; I want `cargo doc-portal open dep-name` to jump straight there.”
- Offline dev: “I want local `std` docs and my crate docs cross-linked.”

# Prior art (and why it’s insufficient)
- Users manually browse `target/doc/` or rely on browser search; this doesn’t scale.
- Existing issues and threads demonstrate the *desire* for `cargo doc crate-name` / workspace doc homepages, but there isn’t a turnkey solution.

# Design goals
- Generate a **portal index** page that lists:
  - workspace crates (with one-line summaries)
  - direct deps + a searchable “all crates in tree” list
- Provide `cargo doc-portal open <crate>` and `cargo doc-portal serve` for offline navigation.
- Optional: integrate local `std` docs into the portal (best-effort, configurable).

# Non-goals
- Replacing rustdoc’s HTML output.
- Solving docs.rs hosting.

# Architecture & API sketch
- CLI wrapper:
  - `cargo doc-portal build [cargo doc args…]`
  - `cargo doc-portal open [crate]`
  - `cargo doc-portal serve [--port]`
- Implementation:
  1. Run `cargo doc` (possibly with `--workspace`).
  2. Parse `cargo metadata` to learn workspace members + resolved deps.
  3. Detect generated docs locations under `target/doc`.
  4. Emit `target/doc-portal/index.html` with:
     - workspace section
     - dependency section
     - search box (static JS)
     - links into rustdoc pages (and optionally local `std`)
- Optional enhancement: if `-Z rustdoc-map`/extern-map data is available, use it to improve cross-links.

# Security / safety model
- “Static site generation” only (no network required).
- If `serve` exists, bind to localhost by default and avoid directory traversal.

# Maintenance & governance plan
- Keep portal output stable and dependency-light (pure HTML + small JS).
- Treat Cargo/rustdoc output as semi-stable: include a compatibility test matrix of fixtures (workspace shapes, duplicate deps).

# Milestones
- 0.1: generate portal index + `open` for workspace crates.
- 0.2: dependency browsing (`open dep`) + search across docs.
- 0.3: optional `std` linkage + external map integrations.

# Open questions
- Best discovery of local `std` docs across platforms/toolchains.
- Handling duplicate crate names / multiple versions (link strategy).

# Sources
See front matter links.
