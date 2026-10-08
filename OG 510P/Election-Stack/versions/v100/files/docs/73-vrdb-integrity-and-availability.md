# VRDB integrity and availability (registration is a Tier‑0 target)

**Track:** A (Deployable core)


This doc extends the PBB/E2E design to cover **voter registration databases (VRDBs)** and related eligibility services.

## Why this matters
If an attacker can (a) flip eligibility, (b) alter precinct mapping/ballot style, or (c) take registration check‑in offline on election day, they can create **real disenfranchisement** and **instant legitimacy collapse** without ever touching encrypted ballots.

NIST identifies VRDB information types (names/addresses, IDs, precinct mapping, status, voter history) and rates confidentiality/integrity/availability impacts as **moderate** — meaning failures are serious but often underappreciated operationally. (See NIST “Security of Voter Registration Databases”.)

## Threats (paranoid list)
- **Integrity attacks:** eligible→ineligible, precinct remap, party/UOCAVA status flips, duplicate registrations, targeted “inactive” flags
- **Availability attacks:** check‑in outages; same‑day registration systems degraded; selective regional DoS
- **Confidentiality attacks:** voter PII theft for intimidation, phishing, coercion, disinfo
- **Insider + vendor + supply‑chain compromise:** managed services, software updates, remote support tooling
- **Disinformation:** false “VRDB hacked” claims intended to erode trust (plan for evidence + comms)

## Invariants (MUST)
1. **Ballot style assignment is auditable.** Every issued ballot style is reproducible from published rules + signed snapshots.
2. **Eligibility changes are explainable.** Each eligibility-affecting change has a reason code and is attributable to an authenticated actor/process.
3. **Mass-change events are detectable.** Large deltas trigger automatic alerts and require ceremony-level review.
4. **Election-day continuity.** Pollbook/check‑in can operate from signed offline snapshots with documented reconciliation.

## Architecture (high level)
- VRDB remains an administrative system, but publishes **signed, privacy-preserving snapshots** and a **change-transparency log**:
  - **VRDB Snapshot**: signed hash of canonicalized records (or partitions) for pollbook use
  - **Change Log**: append-only entries describing eligibility-affecting changes (content-addressed)
  - **Witnessing**: independent monitors co-sign snapshot roots to prevent “quiet rollback”
- Voters/pollbooks verify using:
  - **Online status proof** (privacy-partitioned) OR
  - **Offline snapshot proof** (for election-day resilience)

## Deployment profiles
- **Profile A (most realistic):** VRDB transparency + offline pollbooks + paper ballot of record + RLAs
- **Profile B:** adds private online voter status proofs (OHTTP/ODoH) for early detection of targeted suppression
- **Profile C (hard mode):** cryptographic membership proofs for eligibility (ZK accumulator), still backed by snapshot/log evidence

## Evidence outputs
- Daily: `VRDBSnapshot + witness cosignatures + notarized hashes`
- Continuous: `VRDBChangeLog + signed DriftAlerts`
- Incident: signed public statements + attached proofs (snapshot roots, log entries, witness disagreement evidence)

## Open questions
- How to publish *useful* public evidence without turning VRDB into a turnout/targeting oracle?
- How to integrate state-by-state legal constraints on registration disclosure while preserving auditability?