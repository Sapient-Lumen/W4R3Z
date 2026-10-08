# 241 — Verifier capacity & distribution (who is watching, and where verification lands)

**Track:** A (Deployable core)

The archive’s core social claim is not “evidence exists.” It is: **evidence is used** under pressure.
That requires a real verification ecosystem during the critical post‑election window (often 24–72h).

This doc is a compact bridge between:
- comms authenticity + time‑to‑refute (`194`, `240`),
- publishable verifier outputs (`193`),
- verifier MVP path (`188`) and offline observer workflow (`177`),
- witness governance + liveness/dissent (`135`),
- Track A pilot reality (`docs/track-a/PILOT.md`).

## 241.1 The failure mode (legibility theater)

A jurisdiction can “adopt” Track A by publishing correct-looking envelopes and registries,
while still failing operationally because **no one is positioned to verify and publish** in time.

If no replayable verifier output appears in the contested window, the project has failed in substance.

## 241.2 Minimal capacity model (what “capacity exists” means)

Capacity exists if, before polls close, all of the following are true:

1) **At least 3 independent verifier orgs** (distinct org classes recommended: newsroom, civil society, campaign/party, academic)
   have pre-positioned the offline verifier workflow and can publish replayable outputs.

2) **A distribution path exists** so verifier outputs reach the public:
   - the official status/rumor-control surface links to digest-anchored verifier outputs, and
   - at least one independent mirror/index can re-publish those digests if official channels are degraded.

3) **Behavioral health is visible**:
   - witnesses/verifiers publish corrections and disagreements when warranted (silence is not evidence),
   - liveness+dissent surfaces exist for witnesses (`hfv.witness.liveness_dissent_report`).

This is intentionally modest: “a few real verifiers, in time, with publishable artifacts.”

## 241.3 Make capacity publishable (so it can’t be pretended)

Publish a verifier-capacity directory as evidence:

- kind: `hfv.verifier.capacity_roster`
- payload schema: `schemas/VerifierCapacityRoster.json`
- template: `artifacts/templates/verifier-capacity-roster-payload.json`

Verifier onboarding template (for newsrooms/watchdogs/campaigns):
- `artifacts/templates/verifier-onboarding-mini-curriculum.md`

The roster is a **directory, not an endorsement**:
- entries may be self-attested,
- the source of truth is the verifier’s published reports (`hfv.verifier.report`, `hfv.verifier.packet_verification_report`),
- the roster exists to answer “who will look?” and “where will their outputs land?” *before the crisis*.

Recommended wiring:
- the status/rumor-control surface (`195`) links to the current roster digest,
- the roster includes report feeds / publication endpoints for each verifier,
- mirrors index roster digests like other public pointer surfaces (`200–205`).


Critical-window flow (time‑to‑refute):
- the authority’s authenticity cell publishes the verdict notice + packet digest quickly (`194.4`, `240`),
- rostered verifiers publish replayable verification output to their **report_feed** (self‑stated `ttr_target_minutes` is the expectation baseline),
- the official status/rumor-control surface links to those verifier outputs by digest, so audiences can follow a single “truth lane” even if social media is chaotic.

## 241.4 Pilot requirement (keep it real)

A Track A pilot SHOULD treat “verifier capacity” as a deliverable:

- publish a capacity roster **before polls close**,
- ensure at least **two** rostered verifiers publish replayable PacketVerificationReports for each public packet you ship,
- record time-to-refute observations (TTR‑1/TTR‑2) and publish them in the pilot after-action report (`artifacts/templates/after-action-report.md`).

Operator checklist: `artifacts/checklists/pilot-after-action-minimum-publishables.md`.

## 241.5 Failure signals

- No capacity roster exists, or it appears only after controversy begins.
- “Verification” is only a press statement (no replayable PacketVerificationReports).
- All “independent” verifiers are monoculture (same provider/funder) and never publish corrections.
- Verifier outputs cannot reach the public without a single platform chokepoint.

Treat these as capability gaps, not PR issues: update the pilot plan, staffing, and partnerships accordingly.
