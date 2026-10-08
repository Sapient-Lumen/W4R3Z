# Frontier salience snapshot — 2026-03-19 (69)

This pass did **not** promote another foreign-package shipping lane.
It did a deliberate **portfolio rebalance** and sharpened a strong under-served product-engineering lane:

- **P-0087 UI Accessibility Doctor Kit** — because Rust now has enough accessibility substrate that the sharper missing value is no longer “somehow expose semantics”, but rather “publish one reviewable answer to whether the authoring-side semantics are coherent, which findings are authoritative, and what regressions should block a release.”

## Main judgment

The next worthy move here was **not** another GUI framework, **not** another platform accessibility adapter, and **not** the observer-side cross-platform capture lab.
Those are either existing substrate or adjacent lanes.

The sharper missing layer is the **authoring-side doctor/gating contract** above today’s substrate, especially once three more facts are kept explicit:

- **semantic contract** — what nodes, names, roles, values, and stable identities the toolkit/app is actually claiming;
- **rule authority** — whether a finding is structural, standards-inspired, toolkit-specific, or still manual-review territory;
- **baseline drift** — whether a rerender or release changed names, roles, focus order, or node identity in ways another maintainer can review without replaying the UI by hand.

That move is better grounded now because:

- **AccessKit** explicitly positions itself as cross-platform accessibility infrastructure for UI toolkits and now lists multiple Rust integrations;
- **accesskit_winit** gives `winit`-based toolkits a platform accessibility adapter;
- **egui** documents an `accesskit` feature flag;
- **kittest** now exists as an AccessKit-powered framework-agnostic testing library;
- the 2025 Rust vision work explicitly recommends doubling down on **supportive interfaces** from crates and helping users get oriented in the ecosystem;
- the 2025 State of Rust survey still says **debugging/productivity** pain matters and that official docs/code remain the main learning surfaces;
- and a recent field survey of Rust GUI libraries still reads like an ecosystem where accessibility, IME behavior, and general polish vary widely.

So the gap is no longer “Rust cannot do accessibility”.
The gap is that teams still rarely get a **reviewable semantic-quality workflow** above the substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0087 UI Accessibility Doctor Kit** — now promoted as one of the clearest end-user product-engineering opportunities because real substrate exists but semantic-quality workflows remain ad hoc.
8. **P-0197 Text Layout & Shaping Conformance Kit** — still a strong cross-stack correctness lab.
9. **P-0027 text-input-kit** — still one of the clearest low-level product-engineering gaps in Rust GUI.
10. **P-0092 GUI Testing & Snapshot Harness Kit** — still a strong shared regression substrate, but less sharply timed than P-0087 right now.
11. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
12. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library-shipping lane.
13. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm contract opportunities.
14. **P-0467 Apple XCFramework & SwiftPM ShipKit** — still one of the clearest Apple-SDK contract opportunities.
15. **P-0499 NuGet Native Interop ShipKit** — still one of the clearest .NET contract opportunities.
16. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-native contract opportunities.

## Why this won over adjacent candidates right now

- It beat **P-0202 Accessibility Capture & Interop Lab** because the archive had already split the lanes, and the authoring-side doctor lane still lacked an implementation-ready `0.1` shape.
- It beat **P-0027 text-input-kit** because text input is still a lower-level substrate problem, while P-0087 can now stand on real shared substrate and deliver a more reviewable near-term product.
- It beat **P-0092 GUI Testing & Snapshot Harness Kit** because some framework-agnostic testing substrate now exists via **kittest**, but the rule-authority/gating layer above it is still missing.
- It beat another **foreign-package ship contract** because the archive had already been drifting toward that frontier and needed a genuine rebalance toward end-user product engineering.

## What changed in the archive

Added:
- `entries/2026-03-19-249.md`
- `meta/frontier-salience-2026-03-19-69.md`
- `meta/ui-accessibility-doctor-product-plan-2026-03-19.md`
- `fixtures/ui-accessibility-kit/semantic-contract.report.schema.json`
- `fixtures/ui-accessibility-kit/rule-authority.policy.schema.json`
- `fixtures/ui-accessibility-kit/baseline-drift.report.schema.json`
- `fixtures/ui-accessibility-kit/scenarios/virtualized_list_recycles_node_identity_and_breaks_diff/`
- `fixtures/ui-accessibility-kit/scenarios/icon_only_button_name_comes_from_tooltip_requires_manual_review/`
- `fixtures/ui-accessibility-kit/scenarios/canvas_textbox_reports_focus_but_not_value_or_selection/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/ui-accessibility-kit.md`
- `fixtures/ui-accessibility-kit/README.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/prioritization.md`

## What this pass deliberately did not do

It did **not** collapse:

- emitted AccessKit-style semantics,
- toolkit-local rule policy,
- testing-library-style tree queries,
- observer-side platform capture,
- and legal/compliance review

into one fake “Rust accessibility support” story.
