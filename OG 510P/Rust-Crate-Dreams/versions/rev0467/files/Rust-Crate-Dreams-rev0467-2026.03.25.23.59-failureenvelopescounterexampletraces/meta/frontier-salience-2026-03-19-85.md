# Frontier salience snapshot — 2026-03-19 (85)

This pass did **not** add another UI-testing harness, another proc-macro framework, or another generic error renderer.
It sharpened a support-surface lane that had become more important as the crate-support stack got stronger:

- **P-0512 Crate Guidance Pack Kit** — because Rust now has real diagnostic-attribute, compile-fail, proc-macro, and rich-diagnostic substrate, but still lacks one boring receiver-facing contract for **message stability**, **guidance channel**, **environment sensitivity**, **recipe witness**, and **release drift**.

## Main judgment

The next worthy move here was **not** more renderer substrate.
That substrate already exists.

The sharper missing layer is the **joined guidance-support contract** above today’s substrate, especially once five facts stay explicit:

- **message-stability truth** — whether a crate promises exact wording, code-level stability, shape-level stability, failure-only proof, or manual review,
- **guidance-channel truth** — whether support arrives via compiler hints, stderr snapshots, proc-macro emission, `miette` metadata, docs anchors, or a mixed path,
- **environment-sensitivity truth** — which parts depend on toolchain, `rust-src`, nightly-only doctest error-code checks, or panic-free proc-macro paths,
- **recipe-witness truth** — whether the smallest good path was actually exercised,
- **release-drift truth** — whether a lane still catches the misuse while the user-facing support surface quietly changed.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces;
- the Rust Reference now makes `#[diagnostic::on_unimplemented]` and `#[diagnostic::do_not_recommend]` concrete and user-facing;
- rustdoc still makes `compile_fail` useful but warns that failing snippets can become valid later;
- rustdoc’s nightly-only error-code checks still make code-level checks more realistic than exact-message promises;
- `trybuild` still warns that compiler rendering can differ with `rust-src` availability;
- `ui_test` still snapshot-tests how bad usage shows up to users;
- `proc-macro-error2` still exposes a real non-`panic!` path while warning that panics bypass displayed errors;
- `miette::Diagnostic` still makes `code`, `help`, and `url` structured, importable support objects.

So the gap is no longer “Rust lacks diagnostics”.
The gap is that teams still rarely get a **reviewable crate-authored early-failure promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is so often missing.
3. **P-0522 Crate Persistence Surface Pack Kit** — still one of the sharpest support-surface lanes now that durable-state promises are specific.
4. **P-0521 Crate Resource Surface Pack Kit** — still a strong support lane because waiting-room truth is concrete now.
5. **P-0524 Crate Example Surface Pack Kit** — still a strong first-success lane.
6. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because support-level and evidence-lineage truth are concrete.
7. **P-0519 Crate Authority Surface Pack Kit** — now much stronger because origin, fallback, and denial behavior are explicit rather than implied.
8. **P-0512 Crate Guidance Pack Kit** — now much stronger because compile-time/early-failure support is framed as message-stability and channel-contract work rather than “better errors somehow.”
9. **P-0518 Crate Observability Surface Pack Kit** — still unusually strong because activation and route truth are explicit.
10. **P-0517 Crate Performance Envelope Pack Kit** — still unusually strong because measurement intent and workload lineage are explicit.
11. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
12. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
13. **P-0483 Public API Readiness Bundle Kit** — still a strong joined release-review lane.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0509** pass because the archive’s support-surface stack still had a weaker answer for “what exactly is promised when this crate fails early?” than for task-first crate selection.
- It beat another **P-0516** configuration pass because setup recipes still sit downstream of a more basic trust question: what exact help should a user expect when they hit the wrong feature/runtime/proc-macro lane?
- It beat more **P-0523** test-surface work because compile-time guidance still needs its own contract above UI harnesses and docs examples.
- It beat more **P-0525** diagnosis work because diagnosis starts after the crate is already running, while compile-time and proc-macro guidance determines whether a user gets oriented at all.

## What changed in the archive

Added:
- `entries/2026-03-19-265.md`
- `meta/frontier-salience-2026-03-19-85.md`
- `meta/crate-guidance-pack-product-plan-2026-03-19.md`
- `fixtures/crate-guidance-pack-kit/message-stability.report.schema.json`
- `fixtures/crate-guidance-pack-kit/guidance-channel.receipt.schema.json`
- `fixtures/crate-guidance-pack-kit/trybuild_rust_src_changes_rendering_without_changing_core_guidance/`
- `fixtures/crate-guidance-pack-kit/nightly_doctest_error_code_is_code_level_not_message_level/`
- `fixtures/crate-guidance-pack-kit/proc_macro_panics_bypass_guidance_channel/`
- `fixtures/crate-guidance-pack-kit/miette_url_exists_but_recipe_witness_missing/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-guidance-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
- `fixtures/crate-guidance-pack-kit/README.md`
