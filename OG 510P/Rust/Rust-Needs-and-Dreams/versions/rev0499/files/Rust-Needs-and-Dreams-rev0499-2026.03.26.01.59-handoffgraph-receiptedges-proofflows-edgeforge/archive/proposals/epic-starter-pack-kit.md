# Epic Proposal: Starter Pack Kit (`cargo starter`)

## One-sentence pitch
Turn Rust starter repos into first-class, refreshable artifacts: declare what kind of repo is being bootstrapped, import the lane/workenv/policy truths that shaped it, render a working tree with explicit ownership, and keep the result diffable over time.

## Deliverables
- `cargo-starter` reference implementation
- Schemas / artifacts:
  - `starter-subject/v0`
  - `starter-sources/v0`
  - `starter-layout/v0`
  - `starter-render-plan/v0`
  - `starter-env-profile/v0`
  - `starter-policy-profile/v0`
  - `starter-support-profile/v0`
  - `starter-overlay/v0`
  - `starter-check-report/v0`
  - `starter-render-report/v0`
  - `starter-refresh-report/v0`
  - `starter-pack/v0`
- Integrations:
  - Atlas / Adoption Decision imports
  - Workspace Environment / Tooling Contract imports
  - Service / CLI / embedded starter lanes
  - Policy / Support / Release imports where relevant
  - optional renderer adapters for `cargo new`, `cargo-generate`, `create-tauri-app`, `dx new`, `cargo lambda new`, `esp-generate`, or plain file-pack renderers
- Docs:
  - starter provenance guide
  - file ownership / overlay guide
  - refresh and org-overlay guide

## Why now (signals)
- Rust’s vision work explicitly says users need help navigating crates.io and says there is no clear place to get advice on a good “starter set” of crates.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online docs remain the canonical reference while LLM/editor workflows are rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `cargo new` is intentionally a simple template rather than a full starter-repo system.
  https://doc.rust-lang.org/cargo/commands/cargo-new.html
- Cargo now inherits workspace fields during `cargo new` / `cargo init`, which means starter repos increasingly encode workspace governance and org defaults from the beginning.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo-generate` already proves that template-driven Rust project bootstrap is real, but it also reveals the current fragmentation: users discover template repos ad hoc.
  https://docs.rs/crate/cargo-generate/latest
- Tauri’s `create-tauri-app`, Dioxus’s `dx new`, Cargo Lambda’s `cargo lambda new`, and `esp-generate` show the ecosystem already has multiple real bootstrap lanes, strengthening the case for a contract above generators rather than one more generator.
  https://v2.tauri.app/start/create-project/
  https://dioxuslabs.com/learn/0.7/tutorial/new_app/
  https://www.cargo-lambda.info/commands/new.html
  https://docs.espressif.com/projects/rust/book/getting-started/tooling/esp-generate.html
- Rust’s 2026 flagships explicitly include public/private dependencies and SBOM support, which means supply-chain posture is moving earlier in the repo lifecycle.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Non-goals
- Replacing `cargo new`, `cargo init`, or `cargo-generate`
- Standardizing one universal starter repo for all Rust domains
- Choosing crates without imported atlas/adoption inputs
- Hiding environment, policy, or support posture inside giant boilerplate bundles
- Turning a rendered git repo into the only source of truth

## Strategic value
Starter Pack Kit has leverage because it connects:
- ecosystem navigation,
- concrete project adoption decisions,
- workspace/environment realization,
- supply-chain and support posture,
- and the repo snapshot that humans and assistants actually touch first.

It also fills a conspicuous hole in the archive: the layer where a recommendation stops being a brief and becomes a **maintainable starting repository**. The extra leverage comes from being adapter-aware: it can sit above both plain Cargo scaffolding and domain-specific bootstrappers without pretending those lanes are the same.

## Milestones
1. **v0**
   - export `starter-pack/v0`
   - support one conservative CLI lane and one service lane
   - stable ownership and freshness reason codes
   - one direct render path and one delegated render path with `starter-render-report/v0`
2. **v0.2**
   - add org overlays and refresh reports
   - add optional adapter lanes for `cargo-generate`-style templates and one domain bootstrapper
   - add support/policy imports
3. **v1**
   - better docs/assistant derivations
   - richer release/workenv/productization integrations
   - conformance corpus for refresh/diff behavior
