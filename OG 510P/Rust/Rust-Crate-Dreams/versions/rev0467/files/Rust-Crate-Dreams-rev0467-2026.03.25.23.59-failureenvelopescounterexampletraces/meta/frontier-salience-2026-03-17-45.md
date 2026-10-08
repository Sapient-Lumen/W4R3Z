# Frontier salience snapshot — 2026-03-17 (45)

This pass did **not** promote a new lane.
It sharpened an existing high-ranked cross-cutting proposal:

- **P-0519 Crate Authority Surface Pack Kit** — because the archive still lacked a good implementation-ready artifact for the ordinary question that sits between “this crate seems useful” and “can we safely adopt it in a sandboxed, offline, deterministic, or policy-constrained setting?”: *what ambient powers does it really assume, which are injectable, and which restricted profiles actually hold up under witness?*

## Main judgment

The next worthy move in this frontier was **not** another sandbox runtime, another capability library, another static scanner, or another general security-score experiment.
Those pieces already exist in partial form or answer a different layer.

The sharper missing layer is the **authority-surface contract** above them:

- named authority budgets,
- named profiles,
- injection-boundary receipts,
- determinism hazards,
- sandbox / offline / fixed-dependency witnesses,
- and release-to-release authority diffs.

That move is now better grounded because:

- the Rust vision-doc work explicitly treats supportive interfaces from crates as part of Rust’s product experience,
- the 2025 State of Rust survey says docs and code remain the main learning surfaces,
- the safety-critical vision-doc post says teams often accelerate with crates first and then explicitly harden, constrain, rewrite, or replace dependencies in production-critical paths,
- the sandboxed build-script goal makes file/network/process authority and determinism pressure an explicit Rust-project concern,
- `ambient-authority` and `cap-std` show that capability-oriented substrate is real and usable,
- `wasi-cap-std-sync` shows that sandboxed capability models can be carried into a host boundary on Unix and Windows,
- `rustix` is explicit that low-level substrate does **not** itself restrict ambient authorities,
- and `getrandom` is explicit that custom or opt-in backends exist, but that library-local configuration does not automatically control downstream behavior.

So the gap is no longer “Rust has no capability substrate”.
The gap is that teams still rarely get a **reviewable budget / injection / witness artifact** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the best support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — now a much more believable `0.1` crate for ambient-power and determinism review.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0521 Crate Resource Surface Pack Kit** — one of the best capacity/support contracts in the frontier.
7. **P-0517 Crate Performance Envelope Pack Kit** — now a strong workload/metric honesty lane.

## Why this won over adjacent candidates right now

- It beat **more security-policy follow-ons** because raw policy and lints still do not tell adopters what a chosen crate actually assumes from the host.
- It beat **more sandboxing substrate ideas** because the missing pain is often reviewability and drift detection, not new isolation machinery.
- It beat **more configuration-scenario follow-ons** because setup recipes still do not answer authority budgets or injection truth.
- It beat several strong **domain workbenches** because this lane multiplies value across CLI, services, embedded, plugin hosts, WASI, SDKs, and regulated software rather than one protocol family at a time.

## What changed in the archive

Added:
- `meta/crate-authority-surface-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-45.md`
- `entries/2026-03-17-225.md`
- `fixtures/crate-authority-surface-pack-kit/README.md`
- `fixtures/crate-authority-surface-pack-kit/authority-budget.policy.schema.json`
- `fixtures/crate-authority-surface-pack-kit/injection-boundary.receipt.schema.json`
- `fixtures/crate-authority-surface-pack-kit/profile-witness.report.schema.json`
- `fixtures/crate-authority-surface-pack-kit/env_or_home_cache_fallback_breaks_offline_profile/`
- `fixtures/crate-authority-surface-pack-kit/seeded_rng_but_system_clock_still_leaks_nondeterminism/`
- `fixtures/crate-authority-surface-pack-kit/cap_std_dir_profile_blocks_absolute_path_escape/`

Updated:
- `proposals/crate-authority-surface-pack-kit.md`
- `fixtures/crate-authority-surface-pack-kit/authority-diff.report.schema.json`
- `fixtures/crate-authority-surface-pack-kit/authority-profile.report.schema.json`
- `fixtures/crate-authority-surface-pack-kit/sandbox-recipe.manifest.schema.json`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- task-first crate choice,
- compile-time sandbox policy,
- capability-oriented runtime substrate,
- generic static authority scanning,
- full sandbox/runtime host platforms,
- and receiver-facing authority-surface contracts

into one fake “better sandboxing” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- https://doc.rust-lang.org/cargo/reference/environment-variables.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://docs.rs/ambient-authority/latest/ambient_authority/struct.AmbientAuthority.html
- https://docs.rs/cap-std/latest/cap_std/
- https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- https://docs.rs/rustix/latest/rustix/
- https://docs.rs/wasi-cap-std-sync/latest/wasi_cap_std_sync/
- https://docs.rs/getrandom/latest/getrandom/
