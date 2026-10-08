# Frontier salience snapshot — 2026-03-19 (84)

This pass did **not** add another sandbox runtime, another capability API, or another static authority scanner.
It sharpened a top-ranked support-surface lane:

- **P-0519 Crate Authority Surface Pack Kit** — because Rust now has real capability, ambient-authority, tempdir, project-dir, entropy-backend, and static-scan substrate, but still lacks one boring receiver-facing contract for **authority origin**, **fallback order**, **refusal posture**, **injection boundaries**, and **profile witnesses**.

## Main judgment

The next worthy move here was **not** more capability substrate.
That substrate already exists.

The sharper missing layer is the **joined authority-support contract** above today’s substrate, especially once five facts stay explicit:

- **authority-origin truth** — where a power actually comes from,
- **fallback-order truth** — which path is preferred before widening into more ambient authority,
- **refusal-posture truth** — what happens when the host denies access,
- **injection-boundary truth** — which dependencies are explicit and where,
- **profile-witness truth** — whether the advertised sandbox/offline/deterministic posture survived a real restriction set.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces;
- `ambient-authority` still makes explicit opt-in to ambient power a first-class API fact;
- `cap-std::fs::Dir::open_ambient_dir` still says it is **not sandboxed** and may access any host-visible path;
- `cap_directories::ProjectDirs::from` still makes project-directory discovery an ambient-authority choice;
- `cap-tempfile` now makes the temp-root decision concrete by offering both ambient `tempdir` and capability-oriented `tempdir_in(&Dir)` routes;
- `getrandom` now makes entropy-origin ownership unusually explicit by saying custom backends belong in the root crate and upstream libraries should not define them outside tests/benchmarks;
- Cargo’s environment and build-script docs still expose large ambient/config surfaces;
- `cargo_capsec` now exists as a real static-scanning prior art lane.

So the gap is no longer “Rust lacks capability or sandbox crates”.
The gap is that teams still rarely get a **reviewable crate-authored authority promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is so often missing.
3. **P-0522 Crate Persistence Surface Pack Kit** — still one of the sharpest support-surface lanes now that durable-state promises are specific.
4. **P-0521 Crate Resource Surface Pack Kit** — still a strong support lane because waiting-room truth is concrete now.
5. **P-0524 Crate Example Surface Pack Kit** — still a strong first-success lane.
6. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because support-level and evidence-lineage truth are concrete.
7. **P-0519 Crate Authority Surface Pack Kit** — now much stronger because origin, fallback, and denial behavior are explicit rather than implied.
8. **P-0518 Crate Observability Surface Pack Kit** — still unusually strong because activation and route truth are explicit.
9. **P-0517 Crate Performance Envelope Pack Kit** — still unusually strong because measurement intent and workload lineage are explicit.
10. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
11. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
12. **P-0483 Public API Readiness Bundle Kit** — still a strong joined release-review lane.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0484** pass because today’s capability/tempdir/project-dir/entropy docs and `cargo_capsec` prior art make the remaining authority gap newly specific.
- It beat another **foreign-package shipping** pass because the archive’s core support-surface stack still had a weaker answer for “where does this power come from and what happens when it is denied?” than for shipping contracts.
- It beat more **observability** or **diagnosis** work because what a crate may touch and how it reacts under denial is still a more foundational adoption-trust question than what it emits once already running.
- It beat another **pathfinder** pass because choice is already strong enough that the next multiplier is improving what happens after adoption, when teams ask “can we actually run this dependency inside our trust boundary?”

## What changed in the archive

Added:
- `entries/2026-03-19-264.md`
- `meta/frontier-salience-2026-03-19-84.md`
- `meta/crate-authority-surface-product-plan-2026-03-19.md`
- `fixtures/crate-authority-surface-pack-kit/authority-origin.receipt.schema.json`
- `fixtures/crate-authority-surface-pack-kit/fallback-chain.report.schema.json`
- `fixtures/crate-authority-surface-pack-kit/refusal-posture.report.schema.json`
- `fixtures/crate-authority-surface-pack-kit/caller_supplied_temp_dir_beats_ambient_temp_root/`
- `fixtures/crate-authority-surface-pack-kit/project_dirs_denied_silently_falls_back_to_tempdir/`
- `fixtures/crate-authority-surface-pack-kit/cache_root_option_loses_priority_to_home_discovery/`
- `fixtures/crate-authority-surface-pack-kit/library_defines_getrandom_backend_instead_of_root_crate/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-authority-surface-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
- `fixtures/crate-authority-surface-pack-kit/README.md`
