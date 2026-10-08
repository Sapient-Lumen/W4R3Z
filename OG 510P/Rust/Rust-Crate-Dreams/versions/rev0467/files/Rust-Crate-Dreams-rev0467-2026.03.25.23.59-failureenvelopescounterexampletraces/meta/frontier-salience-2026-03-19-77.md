# Frontier salience snapshot — 2026-03-19 (77)

This pass did **not** add another docs portal, another tutorial engine, another transcript renderer, or another template generator.
It sharpened a top-ranked support-surface lane:

- **P-0524 Crate Example Surface Pack Kit** — because Rust now has real example/tutorial/docs substrate, but still lacks one boring receiver-facing contract for official quickstarts, prerequisite lineage, docs/example linkage, and witnessed first success.

## Main judgment

The next worthy move here was **not** more substrate.
That substrate already exists.

The sharper missing layer is the **joined first-success contract** above today’s substrate, especially once seven facts stay explicit:

- **quickstart truth** — what the smallest official path actually is,
- **environment truth** — whether that path is local, loopback, credentialed, board/device, browser, or manual-review-only,
- **prerequisite-lineage truth** — where required setup knowledge really came from,
- **success-witness truth** — what counted as proof of life and whether it was actually observed,
- **linkage truth** — whether README, rustdoc, guides, and `examples/` still agree,
- **scenario-coverage truth** — which adoption shapes have an honest official path,
- **normalization-boundary truth** — what dynamic output may be normalized without hiding semantic drift.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces;
- the API Guidelines explicitly warn that example code is often copied verbatim by users;
- Cargo already gives `examples/` first-class target status and compiles them by default under `cargo test`;
- rustdoc already executes documentation examples and has unstable scraped-example support;
- docs.rs already exposes metadata controls and a sandboxed build environment with blocked network access and mostly read-only sources;
- `trycmd` already gives CLI example/testing substrate;
- `term_transcript` already gives transcript-capture substrate;
- `mdBook` already gives guide/book substrate;
- and `cargo-generate` already gives template/bootstrap substrate.

So the gap is no longer “Rust lacks examples”.
The gap is that teams still rarely get a **reviewable crate-authored first-success promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0524 Crate Example Surface Pack Kit** — now a stronger implementation-ready first-success lane because the learning substrate below it is real and the receiver-facing contract above it is still weak.
3. **P-0525 Crate Diagnosis Surface Pack Kit** — still a stronger diagnosis-support lane after the latest pass.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0483 Public API Readiness Bundle Kit** — now a stronger joined release-review lane after the latest pass.
7. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
8. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
9. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
10. **P-0515 Crate Off-Ramp Pack Kit** — still a strong survivability / supportiveness follow-on.
11. **P-0071 MCP Guard Kit** — still a strong modern protocol/deployment-support lane.
12. **P-0012 Desktop ShipKit** — still a strong desktop release/adoption lane.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0520** pass because the support stack still needed a more concrete answer for “first success” before going further into lifecycle promises.
- It beat a deeper **P-0519** pass because authority posture is important, but today’s example/onboarding substrate makes the first-success contract unusually buildable.
- It beat another **foreign-package shipping** pass because the archive already had several fresh shipping-contract revisions and still needed a stronger core supportiveness lane.
- It beat more **pathfinder** work because the ecosystem-choice lane is already strong enough that the archive now benefits more from tightening what happens *after* a crate is chosen.

## What changed in the archive

Added:
- `entries/2026-03-19-257.md`
- `meta/frontier-salience-2026-03-19-77.md`
- `meta/crate-example-surface-product-plan-2026-03-19.md`
- `fixtures/crate-example-surface-pack-kit/README.md`
- `fixtures/crate-example-surface-pack-kit/cli_quickstart/quickstart-path.manifest.example.json`
- `fixtures/crate-example-surface-pack-kit/cli_quickstart/success-witness.receipt.example.json`
- `fixtures/crate-example-surface-pack-kit/async_client_happy_path/adoption-scenario.manifest.example.json`
- `fixtures/crate-example-surface-pack-kit/async_client_happy_path/example-environment.report.example.json`
- `fixtures/crate-example-surface-pack-kit/readme_quickstart_hidden_feature_origin/prerequisite-origin.receipt.example.json`
- `fixtures/crate-example-surface-pack-kit/dynamic_cli_output_normalization/example-normalization.profile.example.json`
- `fixtures/crate-example-surface-pack-kit/guide_book_plus_examples/docs-example-linkage.report.example.json`
- `fixtures/crate-example-surface-pack-kit/proc_macro_getting_started/example-output.report.example.json`
- `fixtures/crate-example-surface-pack-kit/embedded_no_std_demo/example-environment.report.example.json`
- `fixtures/crate-example-surface-pack-kit/credentialed_service_only_path_needs_scenario_honesty/scenario-coverage.report.example.json`
- `fixtures/crate-example-surface-pack-kit/scraped_example_present_but_no_official_success_witness/example-support-check.report.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-example-surface-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
- the relevant scenario READMEs under `fixtures/crate-example-surface-pack-kit/`
