# Authenticity response cell checklist (time-to-refute) — bounded

**Track:** Shared (cross-cutting)


This checklist is for the **critical 24–72h post-election window** when forged screenshots / deepfake “official statements”
can outrun slow institutions.

Goal: publish a **digest-anchored authenticity verdict** faster than rumor spreads (see `docs/194.4`), without amplifying the forged artifact.

Related: `docs/186`, `docs/194`, `docs/195`, `docs/219`, `docs/200–206`, `docs/187`, `artifacts/registries/drill-scenarios.csv`.

---

## A) Pre-election setup (do this before you need it)

- [ ] Name the **authenticity response cell**: operator comms lead + security lead + at least **2 independent monitors**.
- [ ] Ensure all members can fetch and verify:
  - the latest **PublicNotice signing keyset** (`208`),
  - the latest **PublicNotice feed** (`200`) and compute effective state (`220`),
  - parity evidence (`201`) and liveness beacons (`210`) when audiences report divergence.
- [ ] Pre-position an offline-capable verifier workflow (ObserverKit or equivalent) and rehearse the “one-command” path.
- [ ] Pre-publish a short public “how to check” guide that teaches **digest-first verification** (`194.2F`, `195.2`).
- [ ] Set a measurable time-to-refute target (e.g., ≤ 60 min for high-severity forged official statements). Drill it.

---

## B) When a disputed “official statement” appears (do not improvise)

### B1) Triage (60 seconds)
- [ ] Record: where it’s spreading, claimed issuing channel, and claimed time.
- [ ] Do **not** repost the artifact. If you must reference it, describe it abstractly and store it privately for investigators.

### B2) Attempt authentication (5–15 minutes)
- [ ] Fetch the current **PublicNotice feed digest** and **signing keyset digest** from your domain-first bootstrap (`204`) and at least one mirror.
- [ ] Check whether the claimed statement appears as a `PublicNotice` in the feed window (byte-level digest match).
- [ ] If official channels disagree, request monitors emit a bounded `PublicSurfaceParitySnapshot` (`201`) and `LivenessBeacon` (`210`) so “who saw which bytes?” is provable.

### B3) Publish an authenticity verdict (digest-first)
Publish a `PublicNotice` (`notice_type=rumor_control` or `incident_advisory`) that includes:

- [ ] An explicit verdict: **AUTHENTIC / NOT AUTHENTIC / UNCONFIRMED** (use epistemic tags; `218–219`).
- [ ] The relevant digests (feed/keyset/notice digest short forms) and at least two mirror pointers.
- [ ] A “how to verify” section pointing to packet digests and verifier output (not screenshots).
- [ ] A `next_update_at` commitment (make silence diagnosable; `219`, `187`).

If you cannot establish authenticity quickly, publish **UNCONFIRMED** with a short update cadence, then upgrade later. Do not fill gaps with rhetoric.

### B4) Restore parity across surviving channels (15–60 minutes)
- [ ] Require surviving official channels to **re-state the digest** of the verdict notice (parity asserts agreement).
- [ ] If an official channel is compromised, explicitly mark it as compromised in a notice and in the channel directory.

---

## C) After-action (same day)
- [ ] Measure actual time-to-refute vs target; treat miss as a capability gap.
- [ ] Preserve the evidence lane: parity snapshots, liveness beacons, and the verdict notice packet digest.
- [ ] File an AAR (`artifacts/templates/after-action-report.md`) and update drills for the next cycle.
