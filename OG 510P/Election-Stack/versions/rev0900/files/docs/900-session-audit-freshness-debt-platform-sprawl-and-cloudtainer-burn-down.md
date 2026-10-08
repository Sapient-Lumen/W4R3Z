# 900 — Session audit: freshness debt, platform sprawl, and cloudtainer burn-down

**Track:** Shared / Session audit / Release governance

rev0863 is a working-session audit revision. It does not try to convert the archive into current voter guidance or a live-pilot package. It records what looked strong, what looked missing, what looked wasteful, and which corrections should be done first in this cloudtainer.

## Verdict

The release-sealing layer is the strongest part of the datacube. Targeted checks passed for the deterministic release ZIP, manifest closure, release path policy, control-file hygiene, ZIP verifier, safe extractor, byte-for-byte rebuild from stdlib extraction, public-fingerprint warning behavior, publication-receipt channel digests, Ed25519 verifier controls, packet verification report linkage, and size budget.

The operational freshness layer is the weakest part. The lockfile has `1,216` external-source rows, only `118` with SHA-256 byte pins, and `1,098` without byte pins. When the same lockfile is evaluated at the current session date `2026-06-09`, `27` unpinned review windows are already expired, `723` more unexpired rows are due within 30 days, and `717` of those due-in-30 rows are platform/UI/vendor documentation. That is not a voter-instruction failure by itself; it is a maintainer-pressure failure and a warning against treating the cube as current authority.

## What is missing

1. **A current-date dashboard separate from the release-date dashboard.** The baseline go/no-go pack still uses the release-review date preserved from the v862 line. rev0863 adds `artifacts/reports/source-review-pressure-current-rev0863.json` so a maintainer can see what changed by the actual session date without silently rewriting historical release evidence.
2. **A byte-verifiable source cache or mirror lane.** `tools/verify_external_sources_lock.py` found no locally present pinned source bytes to verify in this repo-only cloudtainer. That means pinned rows are structurally described but not independently checkable without a separate cache/fetch process.
3. **A burn-down record for the cloudtainer no-pin queue.** The lockfile contains many notes saying an official route was observed or classified but byte pinning was not added in this cloudtainer. Those should become a first-class queue with decisions: pin, demote, delete, or extend with reviewer/date/rationale.
4. **Live-pilot authority evidence.** The existing no-go packs are correct: local approval, custody/provenance, redaction/publication, accessibility/language, independent review, drill transcripts, signer authority, and production publication governance remain missing.
5. **Explicit AI answer-surface governance.** The archive has many AI/platform surfaces, but should consolidate them into a model/system-card style control: no rights-affecting automated determinations, human approval for official answers, prompt-injection/data-poisoning review, source freshness display, refusal/fallback routes, and public disclosure.
6. **A provenance-vs-truth boundary for C2PA/media-authenticity work.** Provenance metadata can help identify origin and edits, but it must not be documented as proof that content is true, complete, or legally authoritative.

## What should change first

1. **Stop adding broad platform/UI pages until the source-review debt is burned down.** The platform tail is useful as research, but its scale is now the main waste pattern. Replace one-off vendor-page coverage with bounded sampling, high-use surface families, and demotion rules for non-critical UI minutiae.
2. **Patch the review-cliff checks so expired rows cannot hide behind a future-only horizon.** rev0863 updates `scripts/check_current_authority_review_cliff.py` to catch already-expired current-authority windows, not just windows between the release date and the horizon.
3. **Make current-date release checks easy without destroying deterministic historical outputs.** rev0863 lets `tools/release_go_no_go_pack.py` honor `ELECTION_STACK_RELEASE_DATE`; use that for current operator checks while keeping checked-in deterministic baseline packs stable.
4. **Treat source pins as real evidence only when bytes are locally present or fetched under a recorded policy.** Otherwise report them as lockfile commitments, not as verified local bytes.
5. **Preserve the strong sealing layer, but avoid rerunning the whole deep gate blindly.** In this cloudtainer, targeted checks were fast enough; exhaustive all-script runs can become wasteful. Keep a fast integrity gate, a current-source gate, and a slower deep regression lane.

## Speculation and external-context watchlist

Recent public context makes the archive's decentralized-verification emphasis more important. Federal and nonprofit election-security support channels have reportedly changed since the prior release line, so this datacube should assume less centralized coordination and more need for independent mirrors, local official routing, offline verifier transcripts, and witness receipts.

Election technology standards are also moving. VVSG 2.0 is no longer merely theoretical: EAC announced the first VVSG 2.0 certified system in July 2025, while also noting that deployment still depends on state testing, procurement, funding, staff training, and public testing. That should push this cube toward adoption-evidence checklists rather than generic certification prose.

Accessibility and AI governance should be kept current as living lanes. DOJ's Title II web/mobile-app rule, W3C WCAG 2.2 updates, NIST AI RMF/GenAI guidance, CISA CPG 2.0, and C2PA specification updates should be tracked as authority surfaces, not casually copied into voter-facing assertions.

## New rev0863 artifacts

- `artifacts/reports/session-deep-audit-rev0863.json`
- `artifacts/reports/source-review-pressure-current-rev0863.json`
- `artifacts/reports/source-review-pressure-current-rev0863.csv`
- `artifacts/reports/source-review-pressure-rev0863.json`
- `artifacts/reports/current-authority-source-queue-rev0863.json`

Boundary: this audit is maintainer triage. It is not current voter instruction, legal advice, certification evidence, production signer authority, proof of source correctness, proof of source error, or live-pilot authorization.
