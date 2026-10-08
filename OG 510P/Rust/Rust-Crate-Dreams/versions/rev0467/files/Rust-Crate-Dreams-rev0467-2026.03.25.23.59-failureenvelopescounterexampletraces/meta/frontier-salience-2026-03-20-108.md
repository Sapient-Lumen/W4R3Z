# Frontier salience snapshot — 2026-03-20 (108)

This pass did **not** add another ranking heuristic, another security badge, or another crates.io dashboard idea.
It sharpened an older but newly timely ecosystem lane:

- **P-0011 Crate Health Contract Kit** — because Rust now has richer registry/security/publishing substrate, while still lacking one boring maintainer-facing contract for **maintenance windows**, **succession**, **support intent**, and **health-check consistency**.

## Main judgment

The next worthy move here was **not** another popularity score.
That substrate already exists in partial, scattered form.

The sharper missing layer is the **joined crate-health contract** above today’s substrate, especially once four facts stay explicit:

- **maintenance-window truth** — whether the crate is in active feature work, reactive bugfix/security support, critical-fix-only mode, frozen maintenance, or explicitly seeking help,
- **succession-map truth** — whether there is a visible backup path or only one human-shaped point of failure,
- **support-intent truth** — what the crate actually promises about MSRV policy, issue response, security contact, and release expectations,
- **health-check truth** — which parts were maintainer-declared, which parts were imported from registry/tooling surfaces, and which parts remain manual-review territory.

That move is better grounded now because:

- the 2025 State of Rust survey says concern about **developer and maintainer support** ticked upward and explicitly asks companies to support crate authors and contributors;
- the same survey still shows Rust usage at work growing, which means more teams are making dependency choices that need survivability signals;
- crates.io now has a **Security** tab with RustSec advisories visible on crate pages;
- crates.io now supports **Trusted Publishing** for both GitHub Actions and GitLab CI/CD on GitLab.com;
- the 2025 crates.io development update documents crate deletions, publish notifications, report-crate flows, and experimental OpenAPI work as real registry substrate;
- the MSRV-resolver RFC explicitly notes that mutable crates.io metadata could let Cargo report **whether a version is supported**, not just whether a newer one exists;
- and the long-running crates.io issue about moving maintenance status into the UI says the original `Cargo.toml`-bound field can go stale because updating it requires a new release.

So the gap is no longer “Rust has no maintenance metadata story”.
The gap is that teams still rarely get a **reviewable crate-authored health/support/succession promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better choice compounds every later support lane.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because upgrades are where dependency cost becomes real.
3. **P-0515 Crate Off-Ramp Pack Kit** — still strong because leaving a crate cleanly is a concrete receiver-facing need.
4. **P-0011 Crate Health Contract Kit** — now much stronger because registry/security/publishing substrate exists, but support-horizon and succession truth still do not.
5. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown/drain truth remains broadly under-served.
6. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
7. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.

## Why this won over adjacent candidates right now

- It beat a deeper **pathfinder** pass because task-fit choice is already sharper than survivability/support truth after choice.
- It beat another **off-ramp** pass because the archive already had a checked exit-contract lane, but the broader maintenance/support lane was still comparatively underspecified.
- It beat another **trust/security** pass because crates.io now exposes more trust signals, which actually makes the missing support-intent/succession layer clearer.
- It beat a pure **maintainer score** idea because the sharper value is not another heuristic but a reviewable contract that can feed pathfinder, off-ramp, and policy tooling without pretending to be automatic truth.

## What changed in the archive

Added:
- `entries/2026-03-20-288.md`
- `meta/frontier-salience-2026-03-20-108.md`
- `meta/crate-health-contract-product-plan-2026-03-20.md`
- `meta/crate-health-lanes-2026-03-20.md`
- `fixtures/crate-health-contract-kit/README.md`
- `fixtures/crate-health-contract-kit/health-profile.schema.json`
- `fixtures/crate-health-contract-kit/maintenance-window.report.schema.json`
- `fixtures/crate-health-contract-kit/succession-map.report.schema.json`
- `fixtures/crate-health-contract-kit/support-intent.report.schema.json`
- `fixtures/crate-health-contract-kit/health-check.report.schema.json`
- `fixtures/crate-health-contract-kit/quiet_release_stream_but_reactive_support_is_explicit/`
- `fixtures/crate-health-contract-kit/deprecated_lane_without_successor_window_or_backup_fails_health_check/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-health.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
