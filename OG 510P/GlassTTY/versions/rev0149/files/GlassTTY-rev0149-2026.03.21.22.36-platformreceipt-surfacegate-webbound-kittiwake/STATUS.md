# Status

## Current posture

GlassTTY is in a transition from **single-surface bridge with strong evidence tooling** to **multi-surface browser control plane**.

The codebase already has a serious foundation:
- extension + native-host bridge
- CLI and side-panel operator surfaces
- fixture-lab and capture infrastructure
- smoke/readiness/handoff/attempt evidence lanes
- durable archive memory
- a real Claude-oriented adapter path

rev0132 extends that synthesis by adding source-review freshness on top of the approved-source lock and support-source baseline. It still does not claim broad new runtime support.

## Newly settled direction

GlassTTY is officially aiming at:

- six first-class browser surfaces: Claude, ChatGPT, Google AI Studio, Grok, Kimi, Z.ai
- a structured browser state API instead of ad hoc read/write-only surfaces
- proactive drift detection and adaptation infrastructure
- support truth and release gates per surface and workflow
- human-piloted and agent-capable execution
- a cleaner canonical-doc system so future implementers do not have to infer strategy from old handoff notes
- bounded autonomy expansion via explicit policy and laddered operating modes

## What rev0132 adds

This revision adds:

- review-age policy fields on `SUPPORT-SOURCE-LOCK.json` so approved authority has an explicit freshness budget
- stale-review reporting in `support-source-baseline` plus rooted `SUPPORT-SOURCE-BASELINE.json`
- publish-gate checks for stale or missing review on required source refs, plus a stale-lock block so publication cannot ride old authority forever
- refreshed first-party product anchors for Grok, Kimi, and Z.ai based on current web surfaces

## What rev0133 adds

This revision adds:

- `SECOND-ADAPTER-MATRIX.json` so the next adapter choice is backed by explicit scored tradeoffs instead of only prose
- `second-adapter-report` capture/report tooling plus `SECOND-ADAPTER-REPORT.json`
- refreshed research notes that compare current official product/browser surfaces for ChatGPT, AI Studio, Grok, Kimi, and Z.ai
- a locked repo-level decision to keep ChatGPT as the second adapter, with AI Studio next in line once the second-adapter proof lands
- a machine-readable second-adapter execution brief plus a first ChatGPT adapter scaffold so the first proof has ordered phases, artifact targets, and selector discipline


## What rev0142 adds

This revision adds:

- `CHATGPT-PROMOTION-STABILITY-RECEIPT.json` plus `scripts/chatgpt_promotion_stability_receipt.py` so repeated ChatGPT proof windows can be graded for stable support promotion instead of treating one held-quality pass as repeatable truth
- refreshed ChatGPT first-proof-kit, candidate-bundle, support-record, and truth-refresh coverage so the new repeatability gate travels with the existing route/composer/submit/bundle receipts
- `CHATGPT-PLATFORM-ENVELOPE-RECEIPT.json` plus `scripts/chatgpt_platform_envelope_receipt.py` so repeated desktop-web ChatGPT proof cannot silently widen into Windows app, macOS app, iOS, Android, or mobile-web support
- refreshed ChatGPT first-proof-kit, candidate-bundle, support-record, support-source lock, and truth-refresh coverage so the new product-surface gate travels with the existing browser and retention envelope stack


## What rev0146 adds

This revision adds:

- `CHATGPT-BROWSER-ENVELOPE-RECEIPT.json` plus `scripts/chatgpt_browser_envelope_receipt.py` so repeated ChatGPT proof on one explicit lane does not silently widen into Chrome, Edge, Firefox, WebKit, or mobile support
- refreshed ChatGPT first-proof kit, candidate bundle, support record, truth-refresh coverage, and support-source lock so the new browser/project envelope travels with the existing claim/profile/session stack

## What rev0147 adds

This revision adds:

- `CHATGPT-RETENTION-ENVELOPE-RECEIPT.json` plus `scripts/chatgpt_retention_envelope_receipt.py` so repeated ChatGPT proof does not silently blur standard saved-history chats, Temporary Chats, memory-off runs, or reused storage-state sessions together
- refreshed ChatGPT first-proof kit, candidate bundle, support record, truth-refresh coverage, and support-source lock so the new conversation-retention envelope travels with the existing claim/profile/session/browser stack

## What rev0145 adds

This revision adds:

- `CHATGPT-AUTH-WORKSPACE-RECEIPT.json` plus `scripts/chatgpt_auth_workspace_receipt.py` so repeated plain route-first proof cannot silently blur guest, personal, Business, Enterprise, or Edu session stories together
- refreshed ChatGPT first-proof-kit, candidate bundle, support record, truth-refresh coverage, and support-source lock so the new auth/workspace envelope travels with the existing claim/profile stack

## What rev0143 adds

This revision adds:

- `CHATGPT-SUPPORT-CLAIM-RECEIPT.json` plus `scripts/chatgpt_support_claim_receipt.py` so repeated ChatGPT proof does not silently expand into broader browser, auth, or workspace claims without an explicit claim envelope
- refreshed ChatGPT first-proof-kit, candidate-bundle, support-record, selector notes, and truth-refresh coverage so the new claim-boundary gate travels with the existing route/composer/submit/bundle/stability receipts
- `CHATGPT-CAPABILITY-PROFILE-RECEIPT.json` plus `scripts/chatgpt_capability_profile_receipt.py` so repeated lane-bound proof cannot silently expand a plain text-only baseline into Search, uploads, data analysis, voice, image, or other tool-mode support
- refreshed ChatGPT first-proof-kit, candidate-bundle, support-record, selector notes, support-source lock, and truth-refresh coverage so the new model/tool-profile gate travels with the existing claim-boundary stack

## What rev0141 adds

This revision adds:

- `CHATGPT-SUBMIT-WITNESS-RECEIPT.json` plus `scripts/chatgpt-submit-witness-receipt.py` so the route-first ChatGPT baseline can grade dispatch, completion, and latest-turn proof separately from merely typing into the composer
- `CHATGPT-PROOF-BUNDLE-RECEIPT.json` plus `scripts/chatgpt-proof-bundle-receipt.py` so a whole route/composer/submit proof window can be graded for held-bundle promotion instead of promoting isolated receipts
- refreshed ChatGPT first-proof kit, candidate bundle, support record, and rooted truth refresh coverage so the new bundle gate is carried everywhere the route/composer/submit receipts already matter

## What rev0137 adds

This revision adds:

- `CHATGPT-BRANCH-GUARD.json` plus `scripts/chatgpt-branch-guard.py` so the route-first ChatGPT baseline can classify a concrete route witness into continue, continue-with-caution, or stop
- `CHATGPT-COMPOSER-WITNESS-RECEIPT.json` plus `scripts/chatgpt-composer-witness-receipt.py` so the route-first ChatGPT baseline can separate a merely discovered textbox from a proved writable composer with readback evidence
- a history-search vs web-search split so authenticated sidebar search cues are not confused with the search-capable home lane
- rooted capture and refresh support for the new branch guard inside the repo's truth-surface refresh path

## What rev0135 adds

This revision adds:

- `CHATGPT-FIRST-PROOF-KIT.json` plus `scripts/chatgpt-first-proof-kit.py` so the first ChatGPT proof now has a named selector contract, benign exact-match probe, UI branching hazards, and failure taxonomy
- `CHATGPT-POSTURE-MATRIX.json` plus `scripts/chatgpt-posture-matrix.py` so the route-first ChatGPT proof can distinguish baseline-safe home shells from search/home caution variants and richer branch shells
- a named ChatGPT candidate support bundle manifest so the second-adapter bring-up path is now an inspectable queue object rather than only prose and scattered files
- refreshed ChatGPT source lock coverage for current search and GPT-builder branch anchors in addition to web-only composer controls and response actions
- rooted capture and refresh support for the new ChatGPT proof kit and posture matrix inside the repo

## What is implemented today vs planned

### Implemented today
- generic browser↔terminal bridge foundation
- evidence-minded operator tooling and archive discipline
- fixture-lab and capture infrastructure
- readiness/doctor/handoff/attempt lanes
- Claude-first adapter work
- setup-fingerprint / next-action smoke guidance from rev0119

### Designed and seeded by the docs now
- official surface vocabulary and support-record model
- workflow-based support truth
- structured state-family schema and field contracts
- drift and evidence vocabulary
- policy-bound agent model
- autonomy ladder and proof templates
- concrete adoption sequence for future implementers

### Planned, not yet broadly implemented
- parity adapters for ChatGPT, AI Studio, Grok, Kimi, and Z.ai
- canonical structured state families across all official surfaces
- per-surface support records backed by current evidence bundles
- scheduled or operator-triggered drift sweeps
- agent policy/execution/approval records in runtime code
- richer workflow taxonomy beyond “read latest / write prompt / submit”
- consistent promotion/demotion of support tiers based on release-gate evidence

## Truth we should preserve

The repo must continue to distinguish:
- **implemented**
- **evidenced**
- **designed**
- **planned**
- **speculative**

This revision upgrades the designed/planned layers so future implementers can move faster, but it does not blur that line.

## Highest-leverage next moves

1. Adopt the rev0123 doctrine docs and templates as the repo’s living source of truth.
2. Replace the held Claude reference bundle with one current live official-surface support bundle.
3. Execute the ChatGPT first-proof kit on the plain browser route, classify the landed shell with the posture matrix, require the route, composer, submit, and proof-bundle receipts to pass honestly, then repeat the baseline on a second distinct proof window, require the promotion-stability receipt, require the support-claim receipt, require the capability-profile receipt, require the auth-workspace receipt, require the plan-envelope receipt, require the browser-envelope receipt, require the retention-envelope receipt, and finally require the platform-envelope receipt before strengthening support language across tools, auth postures, workspace modes, browsers, conversation-retention modes, or product surfaces.
4. Bind current probe/doctor/readiness outputs into the new state, evidence, support, and navigation vocabulary.
5. Start surface baseline capture and drift comparisons for every official surface, including route/history witnesses where navigation truth matters.
6. Use the new control-plane report as the default fused review surface before broadening support claims.
7. Freeze an install receipt before blaming runtime behavior, and freeze a support-surface snapshot before changing support claims.
8. Keep `OPENING-SURFACE-CONFORMANCE.json`, `SUPPORT-BUNDLE-CONTRACT.json`, `REVISION-RECEIPT-CONFORMANCE.json`, and the truth-surface warning ledger current after meaningful archive changes.
9. Use the support-bundle queue, support publish gate, and validation artifact inventory before widening support language or pruning `validation/latest/*` capture families.
10. Add policy and action/outcome records before allowing autonomous loops.

## Relation to rev0119, rev0121, and rev0122

- rev0119 remains important because its setup fingerprint and next-action guidance are now part of a larger support-truth and evidence system.
- rev0121 established the major product direction and canonical design docs.
- rev0122 made that canon easier to execute by adding templates, vocabularies, seeded support records, and a clearer migration path.
- rev0123 added the operating doctrine that should keep future implementation disciplined rather than merely ambitious.
- rev0124 adds the first concrete fused review tool plus sharper truth-splitting around navigation and durable outcomes.
- rev0125 adds explicit install/bootstrap receipts, frozen support-surface snapshots, and a wake-up path for future operators.
- rev0126 adds a machine-readable opening contract, lineage-aware truth-surface head reporting, and a one-shot truth-surface refresh path that repairs foreign-root latest-capture drift.

- rev0127 adds a revision receipt, compact truth-surface warnings, and a validation artifact-bucket inventory so archive identity, citation risk, and validation sprawl are all machine-visible.

- rev0128 adds support-bundle publication state, a held Claude reference bundle, and release-manifest self-verification so support evidence and handoff payloads are both explicit.
