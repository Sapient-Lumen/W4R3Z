# Design note: Lint Governance Stack (Lint Baseline + Compile Guidance + Edit Workflow + Policy)

## Goal
Define the **division of labor and consumer flow** between declared lint intent, observed findings, debt baselines, reviewable fixes, and downstream verdicts so Rust can improve code-health governance without collapsing everything into one Clippy preset, one CI script pile, or one fake lint score.

This is **not** a new lint engine.
It is a stack note explaining how existing archive pieces should compose:
- [`design/lint-baseline-kit.md`](./lint-baseline-kit.md)
- [`design/compile-guidance-kit.md`](./compile-guidance-kit.md)
- [`design/edit-workflow-kit.md`](./edit-workflow-kit.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/cargo-report-kit.md`](./cargo-report-kit.md)
- [`design/safety-evidence-kit.md`](./safety-evidence-kit.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “linting matters.” They are saying the ecosystem now has **enough real lint-facing surfaces** that the missing problem is governance and handoff:
- Rust’s 2026 flagship plan explicitly includes **safety-critical lints in Clippy**;
- Cargo manifests now support `[lints]`, and workspaces support `[workspace.lints]`, which puts lint policy into reviewable project metadata on stable Rust;
- Cargo is experimenting with `[lints.cargo]`, which means even Cargo-native warnings are moving toward the same control plane;
- Cargo 1.94 added the `cargo report` subcommand and moved future-incompat reporting under that report surface, which makes Cargo-side warning/report families more legible as imports instead of console ephemera;
- Clippy’s current config-file docs still say `clippy.toml` is unstable and may be deprecated, which makes exported profile locks and visible governance artifacts more important than hidden tool-local config;
- `cargo fix` is useful but still constrained by one-configuration-at-a-time analysis, while Cargo is simultaneously elevating auto-fix flows more visibly.

Together these signals justify treating linting as a **stacked execution seam** rather than a loose cluster of Clippy invocations, issue labels, and `cargo fix` folklore.

## Stack layers

### 1) Compile Guidance: maintainer-authored lint and diagnostic intent
Compile Guidance owns the **authored guidance surface**:
- maintainer-authored lint catalogs and policy explanations;
- compile-fail / UI examples showing intended diagnostics or recommended changes;
- stability/support posture for guidance promises;
- hook-profile truth for proc-macro/build/analyzer extensions;
- wording/help/example assets that downstream consumers may render.

Compile Guidance answers questions like:
- “What lint or diagnostic posture is the crate trying to teach or promise?”
- “Which examples define success for a guidance lane?”
- “Which emitted suggestions are explanatory versus machine-applicable?”

Design rule: **authored guidance is not yet observed governance evidence**.
A crate’s lint catalog is not the same thing as the findings observed in a workspace under a concrete toolchain.

### 2) Lint Baseline: selected policy, locked expansion, observed debt, and fix packs
Lint Baseline owns the **observed governance substrate**:
- project-selected lint profiles and their expanded/locked meaning;
- workspace/package lint inheritance posture;
- baseline debt and expiry/review metadata;
- normalized findings from rustc, Clippy, rustdoc, and later Cargo/native adapters;
- diffable finding reports;
- reviewable fix packs and machine-applicability grades.

Lint Baseline answers questions like:
- “Which lint policy did this repo actually select?”
- “Which findings are old debt versus newly introduced?”
- “Which suggested edits are reviewable and under what assumptions?”

Design rule: **baseline artifacts are not verdicts**.
They explain policy selection, findings, and debt posture, but they do not decide whether release, migration, or safety gates pass.

### 3) Edit Workflow: application, selection, and verification of fixes
Edit Workflow owns the **governed application layer**:
- selecting which fixes to apply;
- grouping suggestions into reviewable waves;
- conflict detection and partial-apply posture;
- apply receipts and verification reports;
- human-vs-automatic authority boundaries.

Edit Workflow answers questions like:
- “Which subset of lint fixes did we actually accept?”
- “Was the change wave compiler-driven, rustfix-derived, or manually curated?”
- “What remained unapplied, and why?”

Design rule: **a fix pack is not an edit receipt**.
Suggested changes, selected changes, and verified applied changes are separate truths.

### 4) Policy: explicit gates, waivers, and downstream conclusions
Policy owns the **decision layer**:
- rules and threshold profiles;
- waiver budgets and review requirements;
- release / migration / safety / support consumer-specific conclusions;
- `PASS` / `FAIL` / `INCONCLUSIVE` / `WAIVED` outcomes.

Policy answers questions like:
- “May this package release despite baseline debt?”
- “Do safety-critical profiles require stricter lint subsets than routine CI?”
- “Did this fail because of new findings, drift in profile expansion, or an outdated baseline?”

Design rule: **Policy imports lint evidence; it does not redefine lint findings**.
A lint report may justify a verdict, but it is not itself the verdict.

### 5) Imported and downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **CI/review** can diff new vs baseline findings and attach fix packs;
- **Release / package-admission / migration** workflows can gate on explicit lint evidence instead of console text;
- **Safety Evidence** can import curated safety-critical lint subsets without pretending lint posture is the whole case;
- **Compile Guidance** can stay the authored teaching lane while baselines/reports stay the observed lane.

Design rule: **consumers import slices; they do not collapse authored policy, observed findings, applied edits, and verdicts into one scalar state**.

## What an epic contribution should look like in practice
A worthy contribution here is not “better Clippy defaults” or “a more powerful `cargo fix` wrapper.”
It is a portable, reviewable stack with clear boundaries:

1. **Profile locks first**
   - package/workspace lint posture, group expansion locks, and engine/version identity must be exportable;
2. **Baseline drift second**
   - repos need diffable debt accounting before they need dashboards;
3. **Fixpack + edit-receipt handoff third**
   - suggested edits must remain reviewable and separable from applied edits;
4. **Cargo/future-incompat imports fourth**
   - Cargo-native warning/report lanes should join the same governance story without pretending they are the same as rustc/Clippy findings;
5. **Policy/safety/release consumers fifth**
   - only then should the stack drive gating, release attachments, and safety-heavy profiles.

## Ranked first execution lanes
1. **Workspace/profile-lock lane**
   - best first exporter because stable `[lints]` / `[workspace.lints]` make selected policy reviewable now.
2. **Baseline-drift lane**
   - proves lint governance is more than command-line flags or one CI failure bit.
3. **Fixpack / apply-receipt lane**
   - proves reviewable fixing can stay distinct from observed findings and from final applied edits.
4. **Future-incompat / Cargo-lint import lane**
   - proves Cargo-native report families can join the evidence flow without redefining it.
5. **Safety-/release-consumer lane**
   - proves curated lint evidence can feed real decisions without becoming the whole decision engine.

## Non-goals
- inventing another lint engine;
- forcing one universal lint profile for the ecosystem;
- replacing `cargo clippy`, rustdoc linting, or `cargo fix`;
- treating Cargo future-incompat or Cargo-native lints as identical to compiler and Clippy findings;
- flattening lint evidence into one repo score or “cleanliness” badge.

## Archive implications
- The archive should now treat **Lint Baseline + Compile Guidance + Edit Workflow + Policy** as a coupled **Lint Governance Stack** in frontier discussions, with Cargo Report and Safety Evidence as imported companions rather than competing truth engines.
- Future revisions should prefer **profile locks, explicit baseline debt, fixpack/apply receipts, Cargo/future-incompat imports, and policy handoff** over another Clippy preset, shell-scripted lint gate, or magical autofix story.
- When migration, release, safety, or support work cites lint posture, it should distinguish **authored guidance**, **selected policy**, **observed findings**, **applied edits**, and **downstream verdicts**.

## References (signals)
- Rust in 2026 / flagship themes:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo workspaces and `workspace.lints`:
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo manifest `[lints]` section:
  https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
- Cargo unstable `[lints.cargo]`:
  https://doc.rust-lang.org/cargo/reference/unstable.html#lintscargo
- Cargo changelog (`cargo report` subcommand / future-incompat rename):
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo report`:
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
- `cargo fix`:
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Advanced edition migrations:
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo 1.90 development report (`cargo fix` architecture):
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
