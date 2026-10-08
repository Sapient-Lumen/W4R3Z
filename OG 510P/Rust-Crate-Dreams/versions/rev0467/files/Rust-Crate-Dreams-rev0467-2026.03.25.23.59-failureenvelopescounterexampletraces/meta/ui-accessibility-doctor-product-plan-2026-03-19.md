# UI Accessibility Doctor Kit — product plan (2026-03-19)

This note sharpens **P-0087 UI Accessibility Doctor Kit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps toolkit maintainers and app teams publish one reviewable answer to:

- what authoring-side semantic tree they are actually claiming,
- which checks are structural versus standards-inspired versus toolkit-local,
- which changes since the baseline are expected versus suspicious,
- which findings should block CI or releases,
- and where human/manual accessibility review still begins.

It should **not** try to become a screen reader, a platform accessibility backend, a legal-compliance oracle, or the observer-side capture lab.
Those are substrate or adjacent lanes, not the missing product.

## What the crate should provide other people

For maintainers, QA engineers, release reviewers, and downstream app teams, the crate should provide:

1. **One compact semantic-quality contract** instead of truth spread across toolkit code, issue threads, screenshots, and ad hoc manual checks.
2. **A semantic-contract report** that states what roles, names, focusability, value semantics, and node-identity stability the UI is actually claiming.
3. **A rule-authority policy** that says whether a finding is AccessKit-structural, WCAG/WAI-ARIA/ACT-inspired, toolkit-specific, or still manual-review-only.
4. **A baseline-drift report** that tells another person what changed and whether that drift is likely benign, risky, or ambiguous.
5. **A doctor report and gate result** that can block, warn, or escalate to manual review in CI.
6. **A small bundle** that another maintainer can inspect without replaying the entire app by hand.

## Three first-class review objects

### 1. Semantic contract

This should stay separate from backend/platform capture.

Named classes for `0.1` should focus on authoring-side truth such as:
- `name_present`
- `name_missing`
- `role_declared`
- `focusable_reachable`
- `focusable_unreachable`
- `value_semantics_present`
- `node_identity_stable`
- `manual_review_required`

This object should answer:
- which nodes exist in the authoring-side tree,
- which node ids are meant to remain stable across rerenders,
- where names are explicit versus derived,
- where value/selection semantics exist for text or range widgets,
- and whether focusability/disabled/hidden state still agree.

### 2. Rule authority

This should stop the product from flattening all checks into one fake compliance class.

Named authority classes for `0.1`:
- `accesskit_structural`
- `standards_inspired`
- `toolkit_specific`
- `manual_review_required`

Each rule should also record:
- automation class (`automatic`, `semi_automatic`, `manual`),
- default severity,
- normative or explanatory references,
- and which evidence the rule expects.

### 3. Baseline drift

This should answer questions like:
- did a node name disappear,
- did a role change,
- did focus order change,
- did node identity churn enough to make diffs untrustworthy,
- did a control stay visible/focusable but lose value semantics,
- and is the right conclusion “fail”, “warn”, or “manual review required”?

## Recommended `0.1` command surface

### `cargo a11ydoctor inspect`
Read AccessKit-shaped semantics from a toolkit/app integration and emit normalized authoring-side observations.
This should work for local examples, tests, or fixture replays.

### `cargo a11ydoctor doctor`
Run the rule set against the current semantic contract and emit:
- `semantic-contract.report.json`
- `a11ydoctor.report.json`

### `cargo a11ydoctor diff <old> <new>`
Compare two snapshots and classify:
- `node_added`
- `node_removed`
- `name_changed`
- `role_changed`
- `state_changed`
- `focus_order_changed`
- `node_identity_changed`
- `manual_review_boundary_changed`

### `cargo a11ydoctor gate`
Evaluate drift plus findings against a policy pack and produce:
- `a11ygate.result.json`

### `cargo a11ydoctor bundle`
Produce one compact `.a11ydoctor.zip` containing reports, summaries, and fixture references.

## Recommended crate/workspace split

- `a11ydoctor_model`
  - shared types for contracts, rules, findings, drift, and gate results
- `a11ydoctor_accesskit`
  - extraction/import helpers for AccessKit-shaped trees and stable ids
- `a11ydoctor_rules`
  - built-in rules plus rule-authority metadata
- `a11ydoctor_diff`
  - semantic diffing and identity-stability checks
- `a11ydoctor_render`
  - markdown summaries, overlays, and zip export
- `cargo-a11ydoctor`
  - user-facing CLI / cargo subcommand

Optional later adapters:
- `a11ydoctor_egui`
- `a11ydoctor_slint`
- `a11ydoctor_bevy`
- `a11ydoctor_kittest_import`

## `0.1` artifact set

Core artifacts should be:
- `a11ydoctor.toml`
- `toolkit-profile.json`
- `semantic-contract.report.json`
- `rule-authority.policy.json`
- `a11ydoctor.report.json`
- `baseline-drift.report.json`
- `a11ygate.result.json`
- `notes.md`

This pass says `0.1` also needs one sharper support artifact:
- `manual-review-zones.report.json`

That matters because the kit gets vague again if it only records automatic findings without clearly naming the checks that still require human review.

## Discovery order

1. **Toolkit profile import**
   - toolkit/app identity
   - semantic source
   - ruleset and waiver policy
2. **Semantic contract capture**
   - node ids
   - names/roles/states
   - value/selection semantics
   - focus graph hints
3. **Rule-authority application**
   - structural rules
   - standards-inspired rules
   - toolkit-specific rules
   - manual-review zones
4. **Doctor findings**
   - severity assignment
   - suggested next actions
5. **Baseline drift**
   - compare names/roles/states/focus/node identity
6. **Gate + bundle**
   - CI/release verdict
   - compact summary and archive

## Ranking discipline

The first implementation should not treat “the UI rendered and a tree existed” as the verdict.
A good `0.1` should keep separate:
- `semantic_contract_known`
- `rule_authority_known`
- `baseline_drift_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- AccessKit core tree model and adapters
- AccessKit `winit` integration patterns
- toolkit-native AccessKit integrations such as `egui`
- AccessKit-based testing substrate such as `kittest`
- WCAG/WAI-ARIA/ACT-inspired rule shape

### Do not flatten into one fake verdict
- “an AccessKit tree exists”
- “the toolkit compiles with accessibility enabled”
- “a query-based test passed once”
- “the role looks plausible”
- “the app has no doctor findings so it is legally compliant”

## Preferred proving grounds

- a dialog where an actionable control loses its accessible name
- a virtualized list where node ids churn and diff quality collapses
- a custom/canvas text widget that can focus but does not expose value or selection semantics
- an icon-only control where the accessible name depends on a fragile tooltip/label derivation and should stay manual-review-only

## Non-goals

- not another GUI framework
- not another platform accessibility adapter
- not a full accessibility capture/replay lab
- not a legal/compliance certification tool

## MVP API sketch

```rust
pub enum RuleAuthorityClass {
    AccesskitStructural,
    StandardsInspired,
    ToolkitSpecific,
    ManualReviewRequired,
}

pub fn inspect_semantic_contract(root: &Path) -> Result<SemanticContractReport>;
pub fn evaluate_rules(contract: &SemanticContractReport, policy: &RuleAuthorityPolicy) -> Result<DoctorReport>;
pub fn diff_contracts(old: &SemanticContractReport, new: &SemanticContractReport) -> BaselineDriftReport;
pub fn evaluate_gate(report: &DoctorReport, drift: &BaselineDriftReport, policy: &GatePolicy) -> GateResult;
pub fn write_bundle(bundle: &A11yDoctorBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow AccessKit and its adapters closely.
- Treat `kittest` as important adjacent substrate, not as the whole product.
- Keep standards-inspired rules clearly labeled as such.
- Preserve `manual_review_required` whenever the crate cannot safely infer semantic meaning.

## Sources

- https://accesskit.dev/
- https://docs.rs/crate/accesskit_winit/latest
- https://docs.rs/egui/latest/egui/
- https://docs.rs/kittest/latest/kittest/
- https://www.w3.org/TR/WCAG22/
- https://www.w3.org/TR/act-rules-format/
- https://www.w3.org/WAI/standards-guidelines/act/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
