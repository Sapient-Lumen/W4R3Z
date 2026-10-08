# PublicNotice feed monitoring checklist (integrity + parity + convergence)

This checklist turns `200` + `220` + `221` into an operator routine.
Use it for continuous monitoring of official comms channels.

**Related:** `CHECK:artifacts/checklists/audience-parity-monitoring-checklist.md`; `DOC:docs/203-official-channel-directory-as-evidence.md`; `DOC:docs/201-public-surface-parity-snapshots.md`


## 1) Bootstrap (before election season)
- [ ] Pin the official channel set and “latest feed” locations (`203`, `200`, `204`).
- [ ] Choose a polling cadence + timeouts and document them (`08`).
- [ ] Choose a holdback window for propagation delays (`221`).
- [ ] Choose a verifier profile for what “valid” means (receipts/attachments) (`188`, `193`).
- [ ] Confirm your monitor can emit a publishable parity snapshot (`201`) and a bounded PublicNotice describing mismatches (`186`, `219`).


## 2) Continuous checks (every poll cycle)
**Integrity**
- [ ] Fetch the latest feed per channel; verify digest + envelope parsing (`200`).
- [ ] Detect rollback/rewrite (unexpected chain break / head regression); record as anomaly (`200`, `205`).
- [ ] Fetch any referenced notices/attachments; verify digests and required attachments (`186`, `180`).

**Convergence**
- [ ] Compute “effective current state” via `220` (heads + attached corrections).
- [ ] Compare effective state across channels (`221`).

**Classification**
- [ ] If mismatch is within holdback: mark as “pending propagation” (`221`).
- [ ] If mismatch exceeds holdback: treat as parity failure and begin incident routine (`201`, `186`).


## 3) Parity failure incident routine (bounded)
- [ ] Capture a `hfv.public.surface_parity_snapshot` from all channels (`201`).
- [ ] Publish a PublicNotice describing the mismatch and referencing:
  - [ ] the snapshot digest, and
  - [ ] the mismatching feed/notices digests (`186`, `219`).
- [ ] If relevant, open a claim card for the allegation and pin scope boundaries (`217`, `218`).
- [ ] If monitors disagree on what they saw, treat it as a monitor accountability event (`131`, `136`, `140`).


## 4) Recovery + follow-up
- [ ] Publish a corrective PublicNotice (do not edit-in-place) (`219`, `220`).
- [ ] Ensure all channels converge on the corrected effective state within the holdback window (`221`).
- [ ] After resolution, publish a short “what changed” notice with tags + confidence (`218`, `219`).
