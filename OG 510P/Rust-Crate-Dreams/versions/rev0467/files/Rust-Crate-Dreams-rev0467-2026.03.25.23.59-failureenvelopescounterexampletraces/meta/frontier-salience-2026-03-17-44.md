# Frontier salience snapshot — 2026-03-17 (44)

This pass did **not** promote a new lane.
It sharpened an existing high-ranked cross-cutting proposal:

- **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — because the archive still lacked a good implementation-ready artifact for the ordinary question that sits between “Cargo can search crates” and “a team can responsibly freeze a starter stack”: *for this task, under these constraints, which crates are plausible, what are the trade-offs, and where is manual review still required?*

## Main judgment

The next worthy move in this frontier was **not** another popularity ranker, another general search rewrite, another blog-style curation list, or another attempt to settle official blessing politics.
Those pieces either already exist in partial form or fail for governance reasons.

The sharper missing layer is the **task-oriented decision contract** above them:

- task profiles,
- evidence-weight policies,
- role-coverage reports,
- interop / lock-in reports,
- decision-axis reports,
- starter-set locks,
- and release-to-release decision diffs.

That move is now better grounded because:

- the Rust vision-doc work explicitly treats crate discoverability and supportive ecosystem surfaces as part of Rust’s real product experience,
- the 2025 State of Rust survey says docs and code remain the main learning surfaces,
- the 2024 project-goals notes still call out spotty ecosystem support and the need to assemble learning workflows,
- Cargo search still documents textual search plus descriptions rather than task-aware recommendations,
- Cargo add still optimizes for adding a chosen dependency rather than choosing among plausible families,
- Cargo manifest metadata still gives only small keyword/category slots,
- the crates.io search discussion explicitly says improving search ranking is non-trivial and that present ordering still fails some newcomer expectations,
- and the historical Rust Platform follow-up is still a useful warning against trying to solve discoverability by one giant blessed snapshot.

So the gap is no longer “Rust has no registry or metadata”.
The gap is that teams still rarely get a **reviewable task / role / constraint / lock-in / uncertainty artifact** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — now the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the best support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
5. **P-0521 Crate Resource Surface Pack Kit** — one of the best capacity/support contracts in the frontier.
6. **P-0517 Crate Performance Envelope Pack Kit** — now a strong workload/metric honesty lane.
7. **P-0472 Docs.rs Build Parity Evidence Kit** — critical adjacent lane, but narrower than task-first crate choice.

## Why this won over adjacent candidates right now

- It beat **more support-surface follow-ons** because task selection still precedes most downstream support contracts.
- It beat **more Cargo/build explainability work** because the user pain here is earlier: selecting a stack before maintaining it.
- It beat **more façade-crate ideas** because façade curation is downstream of task-first evidence rather than a substitute for it.
- It beat **more trust/health follow-ons** because those lanes inform selection but do not decide ergonomic or interop fit by themselves.
- It beat several strong **domain workbenches** because this lane multiplies value across CLI, services, embedded, Wasm, GUI, data, and niche stacks rather than one standards family at a time.

## What changed in the archive

Added:
- `meta/crate-ecosystem-pathfinder-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-44.md`
- `entries/2026-03-17-224.md`
- `fixtures/crate-ecosystem-pathfinder-kit/evidence-weight.policy.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/role-coverage.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/decision-axis.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/async_http_service_tokio_lockin_tradeoff/`
- `fixtures/crate-ecosystem-pathfinder-kit/cli_baseline_newcomer_vs_power_stack/`
- `fixtures/crate-ecosystem-pathfinder-kit/embedded_no_std_alloc_split/`
- `fixtures/crate-ecosystem-pathfinder-kit/manual_review_required_conflicting_signals/`

Updated:
- `proposals/crate-ecosystem-pathfinder-kit.md`
- `fixtures/crate-ecosystem-pathfinder-kit/README.md`
- `fixtures/crate-ecosystem-pathfinder-kit/candidate-import.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/interop-surface.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/decision-pack.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/starter-set.lock.schema.json`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- task-first decision packs,
- per-crate health imports,
- trust/risk imports,
- façade crates,
- registry search,
- and official blessing / stdlib-expansion arguments

into one fake “crate curation” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
- https://doc.rust-lang.org/cargo/commands/cargo-search.html
- https://doc.rust-lang.org/cargo/commands/cargo-add.html
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://github.com/rust-lang/crates.io/discussions/9325
- https://internals.rust-lang.org/t/follow-up-the-rust-platform/3782
