# Pilot after-action: minimum publishables (Track A)

**Track:** A (Deployable core)

This checklist keeps pilots real: the after-action output must include **replayable evidence**, not only narrative.

## Must publish (minimum)

1) **After Action Report (AAR)**
   - Template: `artifacts/templates/after-action-report.md`
   - Include: what was actually deployed, what was used in decision-making, and what failed.

2) **Pilot capacity + “who will look”**
   - Publish a verifier capacity roster **before polls close**:
     - kind `hfv.verifier.capacity_roster` (DOC:`241`; template `artifacts/templates/verifier-capacity-roster-payload.json`)

3) **Replayable verifier outputs**
   - For each public packet shipped in the pilot, at least **two** independent verifiers publish:
     - `hfv.verifier.packet_verification_report` (codes-only preferred; DOC:`193`)
   - Include/pin each verifier’s implementation report (`hfv.verifier.report`) when possible.

4) **Witness behavioral health (if witnesses are used)**
   - Publish witness liveness+dissent reports during the post-election window:
     - kind `hfv.witness.liveness_dissent_report` (DOC:`135`)

5) **Time-to-refute observations (if any comms authenticity events occurred)**
   - Record TTR‑1 and TTR‑2 timings (DOC:`240`) and include links to the relevant notice chain + packets.

## Strongly recommended

- Publication compliance evidence for at least one deadline in the cycle (`187`):
  - trigger event + suppression/coverage report when applicable.
- A “split-view note” if any official surface parity anomaly occurred (`201`, `210`).
- COI/funding disclosure evidence for verifiers/witnesses where feasible (`artifacts/checklists/coi-and-funding-disclosure-checklist.md`).

## Red flags (pilot is theater)

- No replayable verifier output appears during the contested window.
- The roster exists only after controversy begins.
- Verifier outputs require trust in a single platform (no offline replay).
