# Public Dependency Boundary Kit — product plan (2026-03-22)

## Product shape

Deliver **P-0431** as:

1. a library for capture / classify / explain / diff / pack;
2. a cargo subcommand for CI and release review;
3. a compact schema family that other tools can import.

## Receiver-facing promise

Given a crate or workspace, another engineer should be able to tell:

- what the manifest intended,
- what dependencies are effectively public today,
- what route caused each exposure,
- what evidence source backs the verdict,
- what current workspace/scope gaps remain,
- and what migration is safest.

## v0.1 commands

- `cargo pub-boundary inspect`
- `cargo pub-boundary explain <dep>`
- `cargo pub-boundary migrate`
- `cargo pub-boundary diff`
- `cargo pub-boundary pack`

## v0.1 artifact set

- `manifest-intent.receipt.json`
- `boundary-verdict.report.json`
- `exposure-route.report.json`
- `evidence-provenance.receipt.json`
- `workspace-gap.receipt.json`
- `boundary-migration.plan.json`
- `public-dependency-drift.diff.json`
- `public-dependency-support-bundle.manifest.json`

## v0.1 implementation stance

- Cargo manifest import and `cargo metadata` import first;
- rustdoc JSON / public-item analysis as optional-but-important evidence;
- explicit exactness classes whenever feature / target / workspace scope is partial;
- migration output should be conservative and non-mutating.

## Stage 1

Freeze verdict taxonomy, route taxonomy, and evidence provenance.
Do not chase resolver futures yet.

## Stage 2

Add migration planning and drift comparison.

## Stage 3

Add richer workspace aggregation, imported lint routing, and edition-migration helpers.

## Adoption targets

1. public libraries with many downstream dependents,
2. multi-crate SDK workspaces,
3. SemVer and release review automation,
4. edition-migration preparation.
