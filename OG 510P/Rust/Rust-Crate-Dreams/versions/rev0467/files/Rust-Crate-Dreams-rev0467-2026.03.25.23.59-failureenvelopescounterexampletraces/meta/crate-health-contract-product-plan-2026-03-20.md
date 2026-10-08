# Crate Health Contract Kit — product plan (2026-03-20)

This note sharpens **P-0011 Crate Health Contract Kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become a global ranking engine, a moral score for maintainers, or a registry-side policy replacement.
It should be a **small crate family plus CLI** that helps maintainers publish one reviewable answer to:

- what support window this crate is really in,
- what support intent is actually being promised,
- what succession path exists if current maintainers step back,
- and which visible registry signals agree or conflict with that story.

The missing value is the **boring health-contract layer** above today’s release dates, badges, security tabs, trusted-publishing settings, issue folklore, and policy discussions.

## What the crate should provide other people

For maintainers, downstream adopters, platform teams, and pathfinder/policy tooling, the crate should provide:

1. **One health profile** instead of scattered README notes, Cargo badges, and repo spelunking.
2. **One maintenance-window report** instead of guessing from the last publish date.
3. **One succession map** instead of “bus factor” folklore.
4. **One support-intent report** instead of vague assumptions about MSRV, issue response, or security-contact posture.
5. **One maintenance-coverage report** that makes invisible work classes legible instead of assuming one health word covers them all.
6. **One compact health-check report** that keeps imported signals, maintainer declarations, and manual-review zones visibly separate.

## Five first-class review objects

### 1. Health profile

Named classes for `0.1` should focus on broad declared posture such as:

- `active_development`
- `reactive_maintenance`
- `critical_fixes_only`
- `frozen_but_supported`
- `seeking_co_maintainer`
- `sunset_in_progress`
- `manual_review_required`

This object should answer:

- whether the profile applies to the whole crate or only a version range,
- whether feature work is expected,
- whether bugfix/security response is expected,
- and where the crate explicitly declines stronger promises.

### 2. Maintenance-window report

Named classes for `0.1` should focus on support-horizon truth such as:

- `active_window_declared`
- `reactive_window_declared`
- `critical_fix_window_declared`
- `support_window_unknown`
- `release_quiet_but_supported`
- `frozen_without_horizon`
- `manual_review_required`

This object should answer:

- which kinds of changes are still in scope,
- whether the crate intends regular releases or only as-needed patches,
- what horizon exists for current supported versions,
- and whether observed registry quietness is consistent with the declared posture.

### 3. Succession map

Named classes for `0.1` should focus on stewardship truth such as:

- `multi_maintainer_with_backup`
- `single_maintainer_with_named_backup`
- `single_maintainer_no_backup`
- `seeking_transfer_or_co_maintainer`
- `organization_owned`
- `successor_crate_declared`
- `manual_review_required`

This object should answer:

- whether there is visible redundancy in stewardship,
- whether a handoff path is documented,
- whether a successor crate or org lane exists,
- and whether downstream users are depending on an undisclosed single point of failure.

### 4. Support-intent report

Named classes for `0.1` should focus on declared support promises such as:

- `msrv_policy_declared`
- `security_contact_declared`
- `issue_response_expectation_declared`
- `release_expectation_declared`
- `trusted_publishing_imported`
- `security_tab_imported`
- `manual_review_required`

This object should answer:

- which support promises are explicit versus imported,
- whether the crate distinguishes best-effort from guaranteed response,
- how security reporting is supposed to work,
- and whether registry trust signals are being over-read as maintainer-support promises.

### 5. Maintenance-coverage report

Named classes for `0.1` should focus on maintenance-duty truth such as:

- `lights_on_only`
- `lights_on_with_partial_enablement`
- `broad_coverage_declared`
- `active_feature_work_but_hidden_maintenance_gaps`
- `critical_fixes_only`
- `manual_review_required`

This object should answer:

- which keep-the-lights-on duties are covered, best-effort, imported-only, or unowned,
- which contributor-enabling duties are covered, best-effort, imported-only, or unowned,
- whether visible activity is masking invisible-work gaps,
- and whether downstream users can honestly rely on more than one broad maintenance label.

## Recommended `0.1` command surface

### `cargo crate-health capture`
Capture maintainer-authored and imported signals and emit:
- `health-profile.report.json`
- `maintenance-window.report.json`
- `succession-map.report.json`
- `support-intent.report.json`
- `maintenance-coverage.report.json`
- `registry-signal.import.json`

### `cargo crate-health check`
Run conservative consistency checks and emit:
- `health-check.report.json`

### `cargo crate-health diff`
Compare two health bundles and emit:
- `health-diff.report.json`

### `cargo crate-health summary`
Render a compact human review note from the structured artifacts.

### `cargo crate-health bundle`
Produce one compact `.cratehealthbundle.zip` containing reports, notes, and selected imports.

## Recommended crate/workspace split

- `crate_health_model`
- `crate_health_import_registry`
- `crate_health_import_repo`
- `crate_health_check`
- `crate_health_diff`
- `cargo-crate-health`

## `0.1` artifact set

Core artifacts should be:
- `crate-health.toml`
- `health-profile.report.json`
- `maintenance-window.report.json`
- `succession-map.report.json`
- `support-intent.report.json`
- `maintenance-coverage.report.json`
- `registry-signal.import.json`
- `health-check.report.json`
- `health-notes.summary.md`

## Discovery order

1. **Import visible signals**
   - latest release and release cadence hints
   - security-tab / RustSec visibility
   - trusted-publishing posture
   - maintainers/owners and org signals
2. **Normalize maintainer intent**
   - active vs reactive vs critical-fix-only
   - supported version windows
   - MSRV and release expectations
3. **Normalize stewardship**
   - backup maintainers
   - org ownership
   - successor/handoff notes
4. **Normalize maintenance coverage**
   - keep-the-lights-on duties
   - contributor-enabling duties
   - named owners versus implied/imported-only coverage
5. **Check consistency**
   - declared support vs visible quietness
   - sunset/successor gaps
   - one-person ownership with no backup disclosures
6. **Bundle export**
   - reports
   - notes
   - manual-review zones

## Ranking discipline

A good `0.1` should not treat “the crate published recently” as the verdict.
It should keep separate:

- `registry_activity_known`
- `security_signal_known`
- `publishing_identity_known`
- `support_intent_known`
- `succession_path_known`
- `maintenance_coverage_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- crates.io Security tab / RustSec visibility
- trusted-publishing settings and provider posture
- publish notification / deletion / report-crate era registry substrate
- Cargo badge and maintenance discussions
- MSRV-aware resolver discussions about supported-version metadata
- repo/docs maintainer notes where available

### Do not flatten into one fake verdict
- “the crate has trusted publishing”
- “the crate has no known RustSec advisory”
- “the crate published recently”
- “the crate has one maintainer”
- “the crate says it is maintained”

## Preferred proving grounds

- a crate with quiet release cadence but explicit reactive support
- a crate that is stable/frozen yet still honestly supported for bugfixes
- a crate with one maintainer but an explicit backup or handoff plan
- a quiet crate with explicit lights-on coverage but weak review capacity
- a fast-moving crate whose invisible maintenance duties are still not owned
- a crate entering sunset without a credible successor or support horizon

## Non-goals

- not a global leaderboard
- not a registry-admin policy engine
- not a social pressure score for maintainers
- not a replacement for pathfinder, off-ramp, or trust tooling

## MVP API sketch

```rust
pub fn capture_health_profile(input: &HealthInput) -> Result<HealthProfileReport>;
pub fn capture_maintenance_window(input: &HealthInput) -> Result<MaintenanceWindowReport>;
pub fn capture_succession_map(input: &HealthInput) -> Result<SuccessionMapReport>;
pub fn capture_support_intent(input: &HealthInput) -> Result<SupportIntentReport>;
pub fn capture_maintenance_coverage(input: &HealthInput) -> Result<MaintenanceCoverageReport>;
pub fn check_health_consistency(bundle: &HealthBundle) -> Result<HealthCheckReport>;
pub fn write_bundle(bundle: &HealthBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Preserve `manual_review_required` as an honest output.
- Keep imported signals distinct from maintainer-authored declarations.
- Compose with pathfinder, off-ramp, and trust lenses instead of blurring into them.
- Prefer mutable, low-friction health files over “cut a new release just to update support posture” assumptions.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- https://doc.rust-lang.org/cargo/reference/manifest.html#the-badges-section
- https://github.com/rust-lang/rfcs/blob/master/text/3537-msrv-resolver.md
- https://github.com/rust-lang/crates.io/issues/2437
- https://internals.rust-lang.org/t/more-metrics-for-crate-maintenance-status-in-crates-io/20855
