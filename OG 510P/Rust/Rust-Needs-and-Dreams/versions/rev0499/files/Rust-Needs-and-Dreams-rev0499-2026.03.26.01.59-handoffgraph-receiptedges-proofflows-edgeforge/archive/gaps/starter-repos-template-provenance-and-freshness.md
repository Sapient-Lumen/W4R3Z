# Gap: starter repos, template provenance, and freshness-aware reference packs

## What is missing
Rust still lacks a **portable, reviewable contract for starter repos**.

The ecosystem now has better ways to **choose** crates and stacks, but it still does not have a shared way to turn those choices into a starter repository that stays understandable over time.

That gap is sharper now because the upstream signals are pulling in both directions at once:
- Rust’s 2025 vision work explicitly says users need help navigating the crates.io ecosystem and do not have a clear place to get advice on a good “starter set” of crates.
- The 2025 State of Rust survey says online documentation remains the canonical reference while LLM-based learning and agentic/editor workflows are rising.
- Cargo’s built-in `cargo new` intentionally creates only a **simple template**.
- The de facto template ecosystem (`cargo-generate`) explicitly works by cloning a pre-existing git repository as a template, and even tells users to find templates via a GitHub topic.
- Cargo now automatically inherits workspace fields when running `cargo new` / `cargo init`, which means project scaffolding is no longer separate from workspace governance and org policy.
- Rust’s 2026 flagship work now pushes public/private dependencies and SBOM support, which means starter repos increasingly encode supply-chain and release posture whether we admit it or not.

What is missing is the layer that says:
- which atlas/adoption lane this starter comes from,
- which workspace/environment/productization truths it imports,
- which files are canonical, generated, or overlay-local,
- what policy/support/release posture it intends,
- how freshness and refresh are handled,
- and what later docs, assistants, or org overlays are allowed to derive from it.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/commands/cargo-new.html
- https://docs.rs/crate/cargo-generate/latest
- https://doc.rust-lang.org/cargo/CHANGELOG.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## The current seam is awkward
Today the path from “this is the stack we recommend” to “here is the repo people actually start from” is fragmented across:
- `cargo new` and ad hoc manual edits,
- `cargo-generate` templates and template repos,
- framework-specific bootstrap commands,
- org-local starter repos,
- copied CI files and lints,
- `.cargo/config.toml`, `rust-toolchain.toml`, devcontainers, Nix flakes, and README notes,
- and increasingly, assistant-generated repository skeletons.

That mixture is workable, but it fails in predictable ways:
- the starter repo has weak provenance,
- the chosen lane and its alternatives disappear,
- environment and policy posture get baked into files without explanation,
- render-path truth disappears once the repo exists,
- generated-versus-owned files drift silently,
- org overlays fork upstream starters instead of declaring deltas,
- freshness is implicit,
- and docs/assistants learn from stale starter snapshots rather than from a canonical derivation boundary.

Rust already has starter-template energy. The problem is not absence of templates; it is absence of a **starter-pack contract** above them.
That is now obvious not only from `cargo new` and `cargo-generate`, but from the spread of domain bootstrap tools such as `create-tauri-app`, `dx new`, `cargo lambda new`, and `esp-generate`. Those tools are evidence for real bootstrap plurality, not evidence that one more generator is the missing contribution.

Sources:
- https://doc.rust-lang.org/cargo/commands/cargo-new.html
- https://docs.rs/crate/cargo-generate/latest
- https://doc.rust-lang.org/cargo/CHANGELOG.html
- https://v2.tauri.app/start/create-project/
- https://dioxuslabs.com/learn/0.7/tutorial/new_app/
- https://www.cargo-lambda.info/commands/new.html
- https://docs.espressif.com/projects/rust/book/getting-started/tooling/esp-generate.html

## Why this matters
A real starter-pack substrate would improve several things at once:
1. **time-to-first-credible-repo** — users need more than a crate name list; they need a repo they can trust and evolve;
2. **freshness and renewability** — starter repos should age visibly, not silently;
3. **org overlays without hard forks** — teams need to add local policy/CI/runtime constraints without losing upstream provenance;
4. **supply-chain posture at the beginning, not later** — if public/private dependencies, SBOM generation, or signing become important, starter repos are where many teams first encode that posture;
5. **better LLM/editor behavior** — assistants should consume declared starter truth, not scrape arbitrary example repos;
6. **cleaner handoff between recommendation and execution** — Atlas / Adoption Decision should not stop at a prose answer when the next real question is “show me the repo we should start from.”

The political point matters too. Rust is already curating starter repos implicitly through tutorials, examples, framework quickstarts, template repos, and social consensus. A starter-pack layer would make that curation more reviewable without pretending one universal bootstrap flow should win.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## What “good” looks like
A worthy contribution here is **not** another template engine, another framework bootstrapper, or a hidden catalog of fashionable starter repos.

It is a **starter-pack kit** with canonical artifacts such as:
- `starter-subject/v0` — what kind of repo this is meant to start;
- `starter-sources/v0` — which atlas/adoption/productization/workenv/policy inputs it imports;
- `starter-layout/v0` — the intended workspace/package/file layout;
- `starter-render-plan/v0` — whether this starter is rendered directly, via `cargo new`, via `cargo-generate`, or via a delegated domain bootstrapper, plus the bounded parameters and expected ownership model;
- `starter-env-profile/v0` — toolchain, config, native-dependency, and local-dev realization posture;
- `starter-policy-profile/v0` — lint, CI, public/private dependency, SBOM, publishing, or admission posture;
- `starter-support-profile/v0` — docs/examples/tests/support envelope the starter intends to begin with;
- `starter-overlay/v0` — org-local substitutions or additions without forking the upstream starter concept;
- `starter-check-report/v0` — what was actually rendered and checked;
- `starter-render-report/v0` — what renderer/adapter/version actually ran, what it produced or delegated, and what local edits or losses remained;
- `starter-refresh-report/v0` — what drifted when the imported sources were re-checked;
- `starter-pack/v0` — the durable bundle consumed by docs, assistants, org platforms, and later archaeology.

The canonical truth should remain the artifact family and its imports. The starter repository itself is a **derived working tree**, not the only source of truth. The render path is also not trivial implementation detail; it needs its own bounded truth so future reviewers can see whether a repo came from direct file rendering, Cargo-native scaffolding, `cargo-generate`, or a delegated domain bootstrapper.

## Why this could be epic
This is the sort of contribution that would look modest at first and then quietly touch a huge part of the ecosystem:
- better onboarding,
- better org-standard starter repos,
- less drift between recommendation and execution,
- clearer workspace/environment/policy ownership,
- and better assistant behavior around “how should this repo start?”

Rust does not just need better advice on what crates to choose. It needs a better way to turn that advice into **fresh, explainable, inheritable starter repos**.
