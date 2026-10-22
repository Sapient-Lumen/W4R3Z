# EvidenceVault archive

EvidenceVault is a curated publication archive for a small paper series plus the artifacts, source trees, and legacy renders needed to audit it.
The canonical papers are the single-file TeX notes under `papers/`; archive navigation, extraction lineage, and bundle provenance stay in metadata.
`SERIES.md` is the sole architecture and reading-order statement. The remaining top-level metadata files are intentionally function-specific: `PAPER_SERIES_INDEX.md` records only titles and layer placement, `CATALOG.md` records only archive lookup, `papers/EXTRACTION_MAP.json` records only uniform per-paper present-state provenance through the concise `from` / `kind` / `note` schema, and `CHANGELOG.md` owns revision-by-revision editorial history. Current revision identity still lives primarily in the archive filename and the top entry of `CHANGELOG.md`; `RELEASE_MANIFEST.json` preserves that exact packaged bundle identity inside the extracted archive, `REVISION_ANCHORS.json` is the compact cross-check for the current revision-bearing surfaces, `REVISION_RECEIPT.json` summarizes the packaged revision delta, `ASSIMILATION_LEDGER.*` preserves which outside patterns were adopted, rejected, or deferred across revisions, `ADR_INDEX.*` preserves standing architecture decisions that should outlive a single revision receipt, `RFC_INDEX.*` preserves bounded unresolved structural proposals that are worth more than one-line deferrals but not yet fit for ADR status, `CURRENT_FRONTIER.*` preserves one bounded live-priority/open-pressure resume surface for repeated comparison-driven passes, `AGENTS.md` gives one compact derivative operating contract, `Makefile` gives one compact derivative command surface, `VALIDATION_INDEX.*` gives one compact assurance/command inventory describing which checks prove what and which builders refresh which governed artifacts, `SOURCE_INDEX.*` gives one compact retained-source and family-representation map, and the other metadata surfaces stay revisionless unless they explicitly govern packaging or standing architecture memory.

## Start here
- `START_HERE.md` — compact operator / LLM bootstrap for careful archive passes.
- `AGENTS.md` — low-entropy derivative repo contract for future careful passes.
- `OPENING_CONTRACT.json` — machine-readable startup and reentry contract.
- `OPENING_SURFACE_CONFORMANCE.json` — machine-readable checklist keeping the opening surfaces aligned.
- `SOURCE_INDEX.md` — compact human-facing retained-source-root and family-representation map.
- `SOURCE_INDEX.json` — machine-readable retained-source-root and family-representation map.
- `CONTROL_SURFACES.json` — machine-readable crosswalk of which surfaces govern what.
- `LIFECYCLE_GATES.json` — machine-readable crosswalk of where startup, revision, comparison-assimilation, release, and packaging checks bite.
- `VALIDATION_INDEX.md` — compact human-facing inventory of checks, wrappers, and refreshed artifacts.
- `VALIDATION_INDEX.json` — machine-readable validation/assurance inventory.
- `CLAIM_OBLIGATION_MAP.md` — compact human-facing map from selected claims to archive obligations and known limits.
- `CLAIM_OBLIGATION_MAP.json` — machine-readable claim-obligation crosswalk.
- `ADR_INDEX.md` — compact human-facing index of standing architecture decisions.
- `ADR_INDEX.json` — machine-readable index of standing architecture decisions.
- `RFC_INDEX.md` — compact human-facing index of bounded unresolved structural proposals.
- `RFC_INDEX.json` — machine-readable index of bounded unresolved structural proposals.
- `CURRENT_FRONTIER.md` — compact human-facing current priority and open-pressure resume surface.
- `CURRENT_FRONTIER.json` — machine-readable current priority and open-pressure resume surface.
- `SERIES.md` — authoritative series architecture and reading order.
- `PUBLISHING.md` — authoritative public-release workflow.
- `PAPER_SERIES_INDEX.md` — compact title index for the published papers.
- `CATALOG.md` — archive lookup for retained sources, curated artifacts, certs, and legacy renders.
- `published/index.md` — public landing page.
- `published/reader_guide.md` — short public reader guide.
- `published/artifact_request.md` — public artifact/request note.
- `published/PUBLIC_SURFACE.json` — machine-readable public-surface manifest.
- `published/releases/RELEASE_INDEX.json` — machine-readable ledger of public releases.
- `published/releases/LATEST.json` — pointer to the latest public release.
- `published/releases/artifacts/ARTIFACT_INDEX.json` — machine-readable ledger of materialized public release bundles.
- `published/releases/snapshots/` — immutable release-scoped public-surface snapshots and historical public-surface authority.
- `release_queue/QUEUE_INDEX.json` — current candidate / hold / published-ready / published queue state.
- `published/README.md` — stable public-facing surface boundary.
- `CHANGELOG.md` — revision history and editorial lineage.
- `REVISION_RECEIPT.json` — compact machine-readable summary of the packaged revision delta.
- `REVISION_ANCHORS.json` — compact machine-readable revision-anchor cross-check for the current bundle/control surfaces.
- `ASSIMILATION_LEDGER.md` — cross-revision map of adopted, rejected, and deferred outside-pattern decisions.
- `RELEASE_MANIFEST.json` — machine-readable packaged bundle identity kept inside the extracted archive.
- `Makefile` — compact checked command wrapper for archive validation, publish-audit, and packaging flows.
- `ARCHIVE_INDEX.md` — concise named bundle lineage for the recent packaged revisions.
- `ARCHIVE_INDEX.json` — machine-readable version of the recent bundle lineage index.
- `CONTEXT_PACK.json` — machine-readable orientation pack for future careful passes.
- `AUDIT/README.md` — audit-surface classification and historical-label rule.
- `papers/EXTRACTION_MAP.json` — per-paper present-state extraction/consolidation provenance in a uniform `from` / `kind` / `note` JSON schema.

## Canonical papers
- `papers/ev_acceptability_kernel.tex` — spine / entry paper.
- `papers/ev_interpretation_profiles.tex` — interpretation bridge.
- `papers/ev_streamfold.tex` — StreamFold / dOCF family note.
- `papers/ev_zkrtp.tex` — zk-RTP family note.
- `papers/ev_pact_ocf.tex` — PACT / OCF family note.

## Editorial boundary
`SERIES.md` is the sole architecture and reading-order statement.
`PUBLISHING.md` is the sole public-release workflow statement.
This file only gives archive entry points and bundle policy. The stable public-facing files themselves live under `published/`, while `OPENING_CONTRACT.json` / `OPENING_SURFACE_CONFORMANCE.json` keep the startup surface explicit, `AGENTS.md` gives a shorter derivative operating contract, `Makefile` gives a compact derivative command surface, `VALIDATION_INDEX.*` keeps the assurance map explicit, `CLAIM_OBLIGATION_MAP.*` keeps selected claim support explicit, `CURRENT_FRONTIER.*` keeps the live comparison priority/deferred-pressure summary explicit, `CONTROL_SURFACES.json` / `LIFECYCLE_GATES.json` crosswalk authority and lifecycle boundaries without replacing the canonical statements, `REVISION_RECEIPT.json` summarizes the packaged delta, `REVISION_ANCHORS.json` keeps current revision-bearing surfaces aligned, `ASSIMILATION_LEDGER.*` preserves cross-revision outside-pattern decisions, `ADR_INDEX.*` preserves standing architecture decisions that should survive multiple revision receipts, `RFC_INDEX.*` preserves bounded unresolved structural proposals, and `RELEASE_MANIFEST.json` / `ARCHIVE_INDEX.*` preserve exact bundle identity and recent named bundle lineage.

## Bundle policy
This archive keeps the published bundle size-conscious:
- no nested upstream zip payloads in the shipped tree (their digests are tracked in `UPSTREAM_INPUTS.sha256`),
- compiled binaries removed in favor of source where possible,
- redundant transient build products pruned when they are not part of the reviewable archive,
- exact duplicate legacy render mirrors pruned when one canonical retained PDF path already remains.
- exact curated artifact mirrors pruned when the same bytes already live at a retained source or cert path, with compact `CANONICAL_PATHS.json` indexes left behind at the old curated lookup location.

Upstream completeness and omissions are tracked in `AUDIT/UPSTREAM_DIFF_REPORT.md`, `UPSTREAM.md`, and `UPSTREAM_COVERAGE.md`.

## Command surface
Run `make help` for the compact checked command surface. In normal maintenance, `make gate` is the shortest truthful wrapper for the archive-wide validation path, `make frontier-check` is the shortest truthful wrapper for current frontier coherence, `make revision-check` is the shortest truthful wrapper for current revision-anchor coherence, `make adr-check` is the shortest truthful wrapper for standing-decision validation, `make rfc-check` is the shortest truthful wrapper for bounded unresolved-proposal validation, `make assimilation-check` is the shortest truthful wrapper for comparison-memory validation, `make validation-check` is the shortest truthful wrapper for assurance/command inventory validation, `make claim-obligation-check` is the shortest truthful wrapper for claim-obligation crosswalk validation, `make publish-audit` is the shortest truthful wrapper for bounded release-materialization/post-refresh audits, `make preflight` is the stricter shipping check, and `make package-release` emits the named archive bundle already described by `RELEASE_MANIFEST.json`. `VALIDATION_INDEX.*` is the compact map when you need to know which target proves what or refreshes which governed artifact; `CLAIM_OBLIGATION_MAP.*` is the compact map when you need to know which selected claims are tied to which surfaces, validators, obligations, known limits, and negative-regression expectations.

## Building papers
Run:
```bash
make build-papers
```
Refreshed PDFs are emitted directly to `papers/*.pdf`; the build runs in transient temp directories so the shipped archive keeps only the canonical compiled paper set and no duplicate convenience mirror.

## Command-runner sequence contract

`COMMAND_RUNNER_SEQUENCE.json` and its exact `COMMAND_RUNNER_SEQUENCE.md` companion now govern composite runner order for `gate`, `publish-audit`, package refresh, and package-final validation. `scripts/validate_command_runners.py` rejects drift between the contract and the runner scripts.
