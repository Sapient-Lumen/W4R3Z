# Adopter slide deck outline (template — 10 slides max)

**Track:** Shared (cross-cutting)

**Purpose:** a compact slide outline for decision-makers (election director, county IT, procurement, legislators, civil society) who will *not* read the full archive.

**Rules (keep this usable):**
- 10 slides max.
- Every load‑bearing claim points to a Track A artifact (doc/checklist/template/example packet).
- Use epistemic tags (`docs/218`) for any statement that is not strictly factual/observed (avoid “likely/probably” without tags).
- State non‑claims early (do not “imply safety”).
- Prefer “what becomes provable under dispute” over features.

---

## Slide 1 — What problem this solves (3 sentences)
- Elections fail most often via **legitimacy collapse**: after a contested result, parties cannot prove what happened.
- Track A adds an **evidence wrapper** around existing paper/BMD workflows.
- Goal: disputes become **faster to settle** (or at least *bounded*) because evidence is portable and independently checkable.

References: `docs/track-a/README.md`, `docs/215-election-lifecycle-evidence-map.md`

## Slide 2 — What this is / what it is not (claims + non‑claims)
- What we claim (hard): dispute‑ready, replayable evidence bundles; anti split‑world publication; offline verification.
- What we do **not** claim: internet ballot return safety; coercion resistance; vendor supply-chain integrity for opaque systems.

References: `docs/166-scope-and-claims-contract.md`, `docs/167-non-claims-and-boundaries.md`

## Slide 3 — The 3-track honesty model
- Track A: deployable evidence infrastructure.
- Track B: hard-mode research (remote return) with explicit non‑claims.
- Track C: North Star (attestation/provenance + anti-capture ecosystem).

References: `docs/154-project-scope-and-track-map.md`, `docs/track-b/README.md`, `docs/track-c/README.md`

## Slide 4 — What changes in operations (additive wrappers)
- Official communications become **signed evidence objects** (PublicNotice).
- Public evidence is published in **small packets** verifiable offline.
- Missingness and selective delivery become **measurable** (coverage/suppression; parity snapshots).

References: `docs/186-incident-communications-as-evidence.md`, `docs/173-canonical-evidence-envelopes-and-packets.md`, `docs/187-publication-compliance-and-coverage.md`, `docs/201-public-surface-parity-snapshots.md`

## Slide 5 — The contested window (24–72h) and time‑to‑refute
- The operational constraint is speed: authentic official statements must be faster to verify than to fake.
- Pre-position a response cell + verifiers + publication surfaces.

References: `docs/240-deepfake-frontier-and-time-to-refute.md`, `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`, `artifacts/checklists/time-to-refute-refutation-packet-checklist.md`

## Slide 6 — Who verifies on behalf of voters (representation duty)
- Most voters will not run verifiers.
- Trust is delegated to **monitors/witnesses/verifiers** whose work is auditable and replayable.

References: `docs/track-a/VOTER_VERIFICATION.md`, `docs/track-a/PERSONS_PATH.md`, `docs/241-verifier-capacity-and-distribution.md`

## Slide 7 — Anti-theater guardrails (how to tell it’s real)
- Offline verification works without vendor services (observer kit succeeds).
- Independent verifier reports exist and can be replayed.
- Missed deadlines become visible (coverage/suppression reports), not just explanations.

References: `docs/177-observer-kit-offline-verification-walkthrough.md`, `docs/193-publishable-verifier-reports.md`, `docs/210-liveness-beacons-and-missingness-surface.md`

## Slide 8 — Minimal pilot (one jurisdiction)
- One county, one election cycle, paper ballots/BMD.
- Deliverables: PublicNotice feed + channel directory + 2 packets + after-action report.

References: `docs/track-a/PILOT.md`, `artifacts/templates/after-action-report.md`

## Slide 9 — Costs / staffing (fill-in)
- Provide local estimates; do not imply this is “free.”

References: `artifacts/templates/adopter-briefing.md`

## Slide 10 — Decision ask
Choose one:
- Pilot Track A wrappers.
- Do nothing (accept weaker dispute evidence).
- Request Track B research (requires explicit non‑claims + promotion protocol).

References: `docs/229-experiment-to-spec-promotion-protocol.md`, `artifacts/templates/procurement-language.md`
