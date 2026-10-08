# MSRV Workspace Lab — product plan (2026-03-20)

This note exists to keep **P-0036 MSRV Workspace Lab** implementation-shaped.
The missing value is no longer “search for one minimum compiler.”
The missing value is a small, reviewable support contract for:

- declared MSRV policy,
- actual resolver-policy activation,
- command-family floors,
- lockfile-authoring floors,
- and concrete blame when those slices diverge.

## The 30-second questions the crate must answer

1. What MSRV policy does this repo **claim**?
2. Was the intended resolver policy **actually active** at the workspace root?
3. Which command families are supported at the policy floor: `build`, `metadata`, `doc`, `update`, `package`, etc.?
4. Does the committed lockfile only preserve old-build reproducibility, or can contributors also **author/update** the lockfile on that floor?
5. If a floor moved, which member, dependency, feature, target edge, edition floor, or lockfile rule explains it?

## Core product surfaces

### 1. `msrv-policy.toml`
Human-authored intent.

Must capture:
- package/member support tiers,
- declared floor(s),
- required command families,
- required targets/features,
- whether pinned-lockfile builds are considered sufficient or only provisional.

### 2. `policy-activation.receipt.json`
Observed truth about whether the intended resolver policy is active.

Must capture:
- workspace kind (`single_package`, `rooted_workspace`, `virtual_workspace`),
- expected policy,
- observed policy,
- activation state,
- where the observed policy came from (`workspace_manifest`, `cargo_config`, env override, default).

### 2b. `effective-workspace-promise.manifest.json`
Normalized support promises after workspace inheritance and policy splitting.

Must capture:
- workspace identifier,
- default promise class,
- per-member promise class,
- declared floor and optional effective floor,
- required command families for each member,
- lockfile-support class,
- activation references and manual-review gaps.

### 2c. `policy-split-diff.report.json`
Receiver-facing drift artifact.

Must answer:
- which member promise changed,
- whether the change was a true floor raise, a split-policy introduction, or only an authoring-lane raise,
- which command families were affected,
- and whether the rest of the workspace promise stayed stable.

### 3. `msrv-observation.receipt.json`
One exact lane observation.

Must pin:
- package,
- command family,
- toolchain,
- target,
- feature profile,
- resolver policy,
- lockfile mode if relevant,
- outcome.

### 4. `command-family-floor.report.json`
Compact receiver-facing summary.

Must answer:
- which commands are supported at the policy floor,
- which require something newer,
- which are only known under a pinned lockfile,
- which are manual-review-only.

### 5. `lockfile-floor.receipt.json`
Separate the update/package/generate path from “still builds from the existing lockfile.”

Must capture:
- action (`read_existing_lockfile`, `generate_lockfile`, `update_lockfile`),
- lockfile version,
- build floor,
- authoring/read floor,
- whether the authoring path is higher than the supported build floor,
- notes on how the floor was derived.

### 6. `msrv-blame.report.json`
Explain divergence conservatively.

Likely finding classes:
- `policy_active`,
- `policy_expected_but_inactive`,
- `dependency_raised_floor`,
- `inactive_target_edge_only`,
- `metadata_floor_higher_than_build_floor`,
- `lockfile_authoring_floor_higher_than_build_floor`,
- `manual_review_required`.

## CLI shape

### `cargo msrv-lab inspect`
Fast path.
No brute-force search.

Produces:
- `policy-activation.receipt.json`
- `lockfile-floor.receipt.json` (if requested)

### `cargo msrv-lab matrix`
Generates the smallest useful lane matrix from policy.

### `cargo msrv-lab capture`
Runs one selected lane and emits `msrv-observation.receipt.json`.

### `cargo msrv-lab summarize`
Produces `command-family-floor.report.json` and a short Markdown summary.

### `cargo msrv-lab blame`
Combines observations into `msrv-blame.report.json`.

### `cargo msrv-lab diff`
Diffs two bundles or two policy states, emphasizing:
- changed activation,
- changed command floors,
- changed lockfile floor,
- changed member promises.

### `cargo msrv-lab pack`
Emits one `msrv-support-bundle.manifest.json` plus the selected receipts and reports for downstream review.

## MVP artifact vocabulary

- `msrv-policy.toml`
- `policy-activation.receipt.json`
- `effective-workspace-promise.manifest.json`
- `toolchain-matrix.plan.json`
- `msrv-observation.receipt.json`
- `command-family-floor.report.json`
- `lockfile-floor.receipt.json`
- `msrv-blame.report.json`
- `resolver-lane.diff.json`
- `policy-split-diff.report.json`
- `msrv-support-bundle.manifest.json`
- `adoption-plan.md`

## Product rules

1. **Never collapse policy activation into policy intent.**
2. **Never collapse build support into metadata/doc/update/package support.**
3. **Never collapse pinned-lockfile buildability into lockfile-authoring compatibility.**
4. **Never claim one repo-wide floor if the policy is member-split.**
5. **Never flatten a single member change into a whole-workspace drift story.**
6. **Prefer `manual_review_required` over fake certainty.**

## Scenario families that should stay in canon

### `virtual_workspace_needs_workspace_resolver3_to_activate_fallback_policy`
Goal: prove that a member’s edition or local expectation is not enough when the root workspace never activates resolver v3.

### `inactive_target_edge_metadata_break`
Goal: prove that an inactive target edge can leave `build` green while `metadata` or related tooling needs something newer.

### `lockfile_v4_update_path_can_raise_authoring_floor_without_raising_build_floor`
Goal: prove that a committed older/pinned lockfile can preserve buildability on an older floor even while `update` / `generate-lockfile` / packaging behavior needs a newer authoring floor.

### `mixed_workspace_policy_split`
Goal: prove that not every workspace wants one MSRV promise.

## What this crate should provide other people

For maintainers:
- a way to publish support policy without lying by compression.

For contributors:
- a fast answer to “why does `build` work here but `metadata`/`update` fails on my toolchain?”

For downstream users:
- a reusable support bundle instead of issue-thread archaeology.

For release/CI engineers:
- a stable artifact family that can gate raises, exceptions, or lockfile-floor drift.

## Non-goals

- Exhaustively searching every feature/target combination.
- Replacing Cargo’s resolver.
- Declaring one universal ecosystem MSRV policy.
- Treating lockfile-floor mismatches as inherently bad; the job is to **make them reviewable**.


## Artifact-completeness additions (2026-03-22)

The lane now needs three more receiver-facing objects to feel complete:

1. **`effective-workspace-promise.manifest.json`** — a normalized view of who in the workspace promises what.
2. **`policy-split-diff.report.json`** — a diff that says exactly which member promise or authoring path changed.
3. **`msrv-support-bundle.manifest.json`** — the portable bundle another reviewer opens first.

Without those, the lane still drifts back toward one-number MSRV folklore.
