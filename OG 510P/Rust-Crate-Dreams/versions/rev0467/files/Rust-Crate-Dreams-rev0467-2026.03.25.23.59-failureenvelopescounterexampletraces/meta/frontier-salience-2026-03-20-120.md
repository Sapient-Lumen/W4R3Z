# Frontier salience snapshot — 2026-03-20 (120)

This pass did **not** open another lint runner, dependency updater, or build-history warehouse.
It deepened **P-0478 Cargo Future-Incompat Triage Kit** by making another release-truth boundary explicit:

- **“the build looked clean” is still too vague unless the crate can say which future-incompat findings were terminal-visible, which were only visible in a full or recalled report, and which remained latent-but-recorded under suppression or recall narrowing.**

## Main judgment

The sharper missing layer is no longer merely “capture + owner + waiver + gate”.
The sharper missing layer is a **finding-visibility / suppression-basis contract**.

Current Cargo and rustc signals make that specific:

1. Cargo's future-incompat chapter still treats the full report as a first-class object that can be revisited later by report id or by rerunning with `--future-incompat-report`.
2. `cargo report future-incompat` can narrow recall to a specific package, which means later visibility can be narrower than the original workspace capture.
3. Cargo config can suppress terminal notifications entirely with `future-incompat-report.frequency = "never"`.
4. rustc's JSON output explicitly says future-incompat diagnostics may still be emitted even when the visible warning was suppressed by `#[allow]` or `--cap-lints`.
5. Cargo's changelog has already needed fixes for duplicate saved reports, reinforcing that recall surfaces need explicit provenance and posture.
6. Rust release notes continue adding new lints to the future-incompat surface, so the distance between “what existed” and “what a reviewer saw” can widen across toolchain eras.

That means the next worthy move is not another generic report viewer.
It is one conservative crate family that can publish:

- **finding-visibility truth**,
- **suppression-basis truth**,
- **latent-debt truth**,
- and **reviewable blame** when terminal cleanliness, recalled reports, and release gates point at different slices of the same underlying debt.

## Why this beat nearby work

The archive already had adjacent lanes for:

- generic fix campaigns,
- semver witness and upgrade-pack work,
- resolver explanation,
- and broad build-analysis history.

What it still lacked was one compact way to say:

- “this blocker existed but was not terminal-visible during the reviewed build,”
- “this report is package-filtered and therefore narrower than the workspace debt surface,”
- and “this finding remains latent debt, not absence of debt.”

That is a real receiver-facing product boundary, not another convenience wrapper around `cargo report`.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
4. **P-0478 Cargo Future-Incompat Triage Kit** — materially stronger after this pass because Cargo/rustc now expose enough report substrate to make latent-debt visibility honest rather than folkloric.
5. **P-0470 Cargo Package Review Kit** — still unusually strong because raw archive authority and extraction truth remain distinct.
6. **P-0477 Cargo Publish Receipt Join Kit** — still unusually strong because post-publish convergence is a different truth from pre-publish review.
7. **P-0036 MSRV Workspace Lab** — still unusually strong because Cargo policy/resolver/lockfile support remains easy to overclaim.
8. **P-0451 Cfg Availability Ledger Kit** — still unusually strong because docs-visible truth remains weaker than usable-support truth.

## What changed in the archive

Added:
- `entries/2026-03-20-300.md`
- `meta/frontier-salience-2026-03-20-120.md`
- `meta/cargo-future-incompat-product-plan-2026-03-20.md`
- `fixtures/cargo-future-incompat-triage-kit/finding-visibility.report.schema.json`
- `fixtures/cargo-future-incompat-triage-kit/suppression-basis.receipt.schema.json`
- scenario families for suppressed-but-recorded latent debt and package-filtered recall narrowing

Updated:
- `README.md`
- `INDEX.md`
- `proposals/cargo-future-incompat-triage-kit.md`
- `fixtures/cargo-future-incompat-triage-kit/README.md`
- `fixtures/cargo-future-incompat-triage-kit/future-incompat.schema.json`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy future-incompat triage contribution for Rust should now provide more than a normalized snapshot and an owner/waiver ledger.
It should provide:

- one explicit **finding-visibility report**,
- one explicit **suppression-basis receipt**,
- and one honest way to keep visible warnings, recall-only findings, and latent-but-recorded debt from masquerading as one review surface.

## Freshness anchors

- Future incompat report — https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- `cargo report` — https://doc.rust-lang.org/cargo/commands/cargo-report.html
- Cargo config — https://doc.rust-lang.org/cargo/reference/config.html
- rustc JSON output — https://doc.rust-lang.org/beta/rustc/json.html
- Cargo changelog — https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust release notes — https://doc.rust-lang.org/beta/releases.html
