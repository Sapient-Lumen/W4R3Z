# Track A pilot (minimal real-world deployment)

**Track:** A (Deployable core)


This file defines a **minimal pilot** for Track A (deployable evidence wrappers around paper/BMD elections).

It is intentionally small: the goal is to learn what evidence is *actually useful* under real operational pressure,
without expanding scope into remote return or North Star assumptions.

## Pilot goals (what success means)

- Produce **portable, independently checkable** public evidence for a real election timeline (pre → election night → canvass/certification).
- Exercise the **human process layer** (comms + triage) so it becomes a capability, not a document.
- End with an after‑action report that names: what worked, what failed, and which evidence was decisive or missing.

## Scope (recommended first pilot)

- One county / one election cycle.
- Paper ballots (or BMD) + existing audit/recount lanes.
- Track A wrappers only (no remote ballot return).


### Supply chain transparency (Track A recommendation; not a pilot blocker)

Track A wraps whatever voting system/EMS the jurisdiction already uses.
If that underlying system is compromised at the supply-chain level, the evidence layer may faithfully record the outputs of a corrupted process.
Track A’s recovery mechanism remains **paper ballot of record + audits/recounts**.

To make disputes meaningfully more resolvable in opaque-vendor environments, the pilot SHOULD also collect/publish (when feasible):
- certified configuration IDs + vendor version strings used during the election,
- a signed software/update/change history from pre-election lock through certification,
- (if feasible) signed hashes of installed packages/firmware images,
- any vendor advisories or emergency changes as PublicNotice items.

Canonical guidance: `docs/17-supply-chain-and-build-integrity.md`.

### Material floor + accessibility (Track A recommendation; not a pilot blocker)

This pilot MUST remain usable when people cannot install tools, cannot stay online, or cannot read long technical documents.
Recommended minimum additions:
- publish one **offline‑verifiable packet** and distribute it via at least one non‑web channel (USB/print/low‑bandwidth mirror) (`177`, `211`),
- publish a one‑page voter‑facing verification story (`docs/track-a/VOTER_VERIFICATION.md`) and keep it discoverable from the README,
- ensure a paper‑of‑record + audit/recount “recovery story” is written in plain language (`docs/track-a/PERSONS_PATH.md`).

## Minimum deployed surfaces (must be public + verifiable)

1) **PublicNotice** (official communications as evidence)
   - Publish a PublicNotice feed and a signing key allow‑list (`186`, `194`, `200`, `208`, `239`).

2) **Official channel directory + bootstrap**
   - Publish the official channel directory and `.well-known` discovery (`203`, `204`).


2.5) **Publication compliance + missingness surface (anti-theater)**
   - Run the **Minimal Adversarial Publication Test (MAPT)** and publish its results (`docs/187`, `artifacts/checklists/minimal-adversarial-publication-test.md`), then log the evaluation (bounded pointers/digests) in `artifacts/registries/mapt-evaluations.csv`.
   - Ensure “silence” produces evidence via **liveness beacons + suppression/missingness reports** (`docs/210`, `docs/181`).
3) **Rumor-control / status board**
   - Run the status surface with uncertainty-safe updates (`195`, `219`, `220`).

4) **Publication compliance**
   - Declare a PublicationContract and emit trigger events + coverage reports (`181`, `187`).

5) **Split-view detection**
   - Produce parity snapshots / liveness beacons during the critical post-election window (`201`, `210`).

6) **Observer Kit packets**
   - Publish at least two small evidence packets that third parties can verify offline (`177`, `211`).

7) **Voting system wrapper transparency (recommended)**
   - Publish certified configuration IDs + vendor version strings used during the election, and an update history (who authorized, when).
   - If available, publish signed hashes of installed packages/firmware images.
   - Publish changes/updates as PublicNotice artifacts.
   - See `17` (Track A wrapper transparency recommendations).

8) **Witness / monitor seed set + disclosure (strongly recommended; required if you deploy witness‑cosigned checkpoints)**
   - Publish the initial witness set and policy as receipted evidence objects (membership + keys + diversity constraints) (`23`, `132`, `135`).
   - Publish public witness/monitor profiles (template: `artifacts/templates/witness-profile.md`) and COI/funding disclosures (`135`).
   - During election week + the 24–72h window, publish at least one **liveness+dissent** report (`hfv.witness.liveness_dissent_report`) so “silence” is not misread as safety (`135`).
   - Name the bootstrapping trust assumption: who selected the initial witness set, and what the plan is to diversify beyond that trust anchor (`139`, `135`).

9) **Verifier capacity roster + report landing**
   - Publish a verifier capacity roster before polls close (kind `hfv.verifier.capacity_roster`; see `241`).
   - Ensure at least two rostered verifiers publish replayable PacketVerificationReports for each public packet.

## Minimum drills (must be run at least once)

Pick three and run them as tabletop or live exercises:
- Conflicting reports / information overload (operator must publish an uncertainty‑safe update).
- Forged “official” statement (time‑to‑refute drill; digest-first response).
- Publication deadline breach (suppression report emitted).

Use the scenario registry: `artifacts/registries/drill-scenarios.csv`.

## Timeline (suggested)

- **T‑90 to T‑30 days:** keys + channel registry + feed bootstrap; recruit a witness/monitor seed set + publish profiles; run comms authenticity drill once.
  - **Admissibility planning:** fill `artifacts/templates/jurisdictional-admissibility-matrix.md` for the venue(s) you might face, add/update a row in `artifacts/registries/admissibility-jurisdiction-index.csv`, and dry‑run one court bundle recipe with a filled worksheet + one‑page crypto primer (`docs/211`).
- **T‑30 to T‑7 days:** publish “how to check” guidance; run overload drill once.
- **Election week:** daily parity/freshness checks; run at least one “forged statement” drill.
- **Post-election:** publish a bounded court-bundle recipe packet for one hypothetical allegation (dry run).

## Outputs (publishable)

- A small set of public evidence packets (each with a manifest digest).
- A public after‑action report (template: `artifacts/templates/after-action-report.md`).
- A pilot‑local admissibility packet: a filled `court-admissibility-worksheet.md` + `crypto-primer-one-page.md` for at least one bundle (may be public or filed as an exhibit depending on jurisdiction).
- Pilot after-action minimum publishables checklist: `artifacts/checklists/pilot-after-action-minimum-publishables.md`.
- If witnesses are used: publish the witness set + witness profiles + at least one liveness+dissent report (`hfv.witness.liveness_dissent_report`; DOC:`135`).
- A short list of “what we would change next cycle.”

## Notes

- This pilot is not a certification effort.
- Do not add new envelope kinds for the pilot; prefer checklists, templates, and example packets.


## Pre-election drills (minimum)
- conflicting_reports_overload
- political_pressure_unverified_claims
- forged_official_statement_time_to_refute