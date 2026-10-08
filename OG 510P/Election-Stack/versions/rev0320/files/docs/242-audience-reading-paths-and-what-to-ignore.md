# Audience reading paths and “what to ignore” (size discipline)

**Track:** Shared

This archive is large and will grow. To keep it usable, treat this document as the *stable map*:
if you only read one “index-like” doc, read this one plus `docs/START_HERE.md`.

## 15-minute orientation (any audience)

1. `docs/START_HERE.md` — what this is, what the three tracks mean.
   - *(Optional for officials/labs/vendors)* `docs/245-external-standards-and-alignment-map.md` — external anchors (VVSG/NIST/CISA)
   - *(Optional)* `docs/263-ballot-design-ballot-building-and-proofing-as-evidence-surfaces.md` — bounded, publishable proof surfaces for ballot production (digests + approvals, no precinct mapping disclosure)
   - *(Optional for officials/mail-voting teams)* `docs/271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md` — logistics integrity digests (privacy-first).
   - *(Optional for officials/mail-voting teams)* `docs/272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md` — intake/verification/opening/scanning rollups (counts-only; anti-weaponization).
   - *(Optional for officials/canvass teams)* `docs/273-ballot-accounting-and-reconciliation-as-evidence-surfaces.md` — end-to-end ballot accounting ledger digests + canvass reconciliation bridges (digest-first; privacy-first).
   - *(Optional for officials/procurement)* `docs/257-supply-chain-procurement-and-vendor-transparency-as-evidence-surfaces.md` (SBOM/provenance/inventory; publishable proofs)
   - *(Optional for maintainers)* `docs/246-assurance-case-skeleton-and-evidence-minimization.md`
   - *(Optional for officials/designers)* `docs/248-accessibility-usability-and-language-access-as-integrity.md` — accessibility + language access as integrity controls. — how to argue trust without archive bloat.
   - *(Optional for ops/comms leads)* `docs/247-ops-security-controls-comms-and-chain-of-custody.md`
   - *(Optional for ops/comms leads)* `docs/259-incident-reporting-and-coordinated-disclosure-as-evidence-surfaces.md` — bounded incident reporting surfaces (digest-first; anti-weaponization).
   - *(Optional for comms leads)* `docs/268-rumor-control-and-mis-disinformation-response-as-evidence-surfaces.md` — bounded rumor-control corrections as verifiable packets (safe pointers; avoids amplification and doxxing). 
   - *(Optional for comms/IT leads)* `docs/261-public-commitments-and-transparency-logs-for-election-evidence.md` — publish hash commitments with append-only history (transparency-log optional), without disclosure.
   - *(Optional for engineering / verification implementers)* `docs/265-canonicalization-signing-timestamping-and-proof-packaging.md` — canonicalize/hash/sign/timestamp (and optionally transparency-log) the repo’s publishable surfaces so independent verification remains stable.
   - *(Optional for policy/administration leads)* `docs/262-jurisdictional-policy-surface-registry.md` — bounded registry of jurisdiction-specific policy knobs (cite-first; no state-by-state bloat).
   - *(Optional for ops leads)* `docs/258-training-tabletop-and-drills-as-evidence-surfaces.md` — publishable preparedness proofs (TTX/drills) without sensitive detail.
   - *(Optional for ops leads)* `docs/276-contingency-planning-and-continuity-of-operations-as-evidence-surfaces.md` — COOP posture, degraded-mode register, dependency digest, and continuity incident capsules (digest-first; anti-targeting).
  - `277-observability-metrics-and-anomaly-response-as-evidence-surfaces.md` (ops-safe telemetry digests + outage capsules; composes with 259/261/265)
   - *(Optional for canvass/provisional leads)* `docs/251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md` — minimal publishable artifacts for provisional/cure/canvass without PII.
   - *(Optional for audit leads / RLAs)* `docs/260-risk-limiting-audits-and-post-election-tabulation-audits-as-evidence-surfaces.md` — publishable audit hashes + digests (randomness/custody/escalation) without ballot/PII disclosure.
   - *(Optional for canvass/certification/recount leads)* `docs/264-recounts-contests-and-certification-disputes-as-evidence-surfaces.md` — bounded publishable surfaces for recounts/contests/certification disputes (declarations, custody attestations, change ledgers), privacy-first.
   - *(Optional for results reporting / ENR leads)* `docs/252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md` — non-finality banner, snapshot packs, and corrections log.
   - *(Optional for test teams / L&A leads)* `docs/255-logic-and-accuracy-and-pre-election-testing-as-evidence-surfaces.md` — publishable proof of pre-election testing without dumps or sensitive configs.
   - *(Optional for registration/VRDB leads)* `docs/269-voter-registration-and-list-maintenance-as-evidence-surfaces.md` — VRDB posture + list maintenance digests (no voter-file dumps; anti-weaponization).
   - *(Optional for in-person operations / EPB owners)* `docs/270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md` — EPB posture + check-in/sync/outage digests (privacy-first; avoid precinct attribution).
   - *(Optional for IT/change-control leads)* `docs/256-software-updates-and-configuration-control-as-evidence-surfaces.md` — configuration baselines, updates, emergency patches, and drift (hashes + attestations).
   - *(Optional)* `docs/254-adjudication-duplication-and-voter-intent-as-evidence-surfaces.md` — how interpretation/duplication stay checkable without PII.
   - *(Optional for security leads)* `docs/249-threat-model-ledger-and-safe-red-teaming.md` — bounded threat modeling + safe red-teaming (non-weaponizing).
2. `docs/166-scope-and-claims-contract.md` — what is asserted.
3. `docs/167-non-claims-and-boundaries.md` — what is explicitly *not* asserted.

## Non-US contexts (scope note)

This archive uses US-style election administration vocabulary in many examples, but most Track A evidence patterns are meant to be portable.
For adaptation notes and open questions (parliamentary/PR/multi-round, non-court dispute lanes), see `docs/172-open-research-questions-and-experiment-backlog.md` (172.9).

## 60-minute adoption screen (election director / county staff)

Read the “outside view” five-item path in `README.md` (it is intentionally strict), then:
- `artifacts/templates/adopter-briefing.md` (planning ballparks + anti-theater guardrails)
- `artifacts/templates/adopter-slide-deck-outline.md` (10-slide outline for commissioners/legislators)
- `docs/track-a/PILOT.md` (what a one-jurisdiction pilot actually looks like)
- `docs/266-physical-security-and-access-control-as-evidence-surfaces.md`
- `docs/267-personnel-security-insider-risk-and-worker-safety-as-evidence-surfaces.md` (physical security + access control as publishable digests; no facility detail leakage)

**If you only pilot one thing:** Track A publication + evidence packaging that survives an outage or dispute.
Do *not* start with Track B/C.

## 60-minute verifier path (newsroom / watchdog / civil society)

1. `docs/188-verifier-minimum-viable-path.md` (the minimal replayable workflow)
2. `docs/177-observer-kit-offline-verification-walkthrough.md` (offline walkthrough)
3. `docs/91-public-verification-and-observer-kit.md` (why the observer kit exists)
4. `docs/240-deepfake-frontier-and-time-to-refute.md` (contested-window posture)
5. `docs/241-verifier-capacity-and-distribution.md` (who is watching, where results land)

Then use:
- `artifacts/templates/verifier-onboarding-mini-curriculum.md` (to train more verifiers quickly)

## 60-minute builder path (tooling / implementation)

1. `docs/166-scope-and-claims-contract.md` (what you may claim)
2. `docs/167-non-claims-and-boundaries.md` (what you must *not* claim)
3. `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`
4. `schemas/` (schema catalog + the payload schemas you need)
5. `docs/179-evidence-api-surface.md` (minimal API surface)
6. `artifacts/examples/` (minimal example packets)
7. `scripts/release_gate.py` (what the archive treats as “valid”)

## What to ignore until needed

This is not a “do not read” list — it is a **size/attention budget** guardrail.

- **Track B** (`docs/track-b/*`) unless you are explicitly doing remote-return research.
- **Track C** (`docs/track-c/*`) unless you are explicitly doing north-star design work.
- **PQC / exotic crypto / deep protocol options** unless you have a deployment plan that requires it.
- **Large registries** unless you are implementing or auditing the toolchain.

When in doubt, stay inside:
- `docs/track-a/*`
- `docs/166-*`, `docs/167-*`
- `docs/188-*`, `docs/177-*`, `docs/91-*`, `docs/187-*`
- `artifacts/templates/*` + `artifacts/checklists/*`

## “If this feels like too much”

That is a signal. Use the 60-minute paths above and insist on a one-jurisdiction pilot with publishable evidence surfaces.
If a proposed requirement cannot be piloted, drilled, or independently replayed, it does not belong in Track A.

## 242.X Observer / poll watcher surfaces (optional)

- If your environment includes partisan watchers or nonpartisan observers, read `docs/250-observation-and-challenge-as-evidence-surfaces.md` for privacy-first, non-interference evidence patterns.

### Data interoperability (when moving results across systems)
- `275-election-data-interoperability-and-schema-registry.md` (digest-first schema/profile commitments; composes with `265` and `261`).
