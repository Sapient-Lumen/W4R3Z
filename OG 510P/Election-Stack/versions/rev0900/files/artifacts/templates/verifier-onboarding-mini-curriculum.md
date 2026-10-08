# Verifier onboarding mini-curriculum (newsroom / watchdog / campaign)

**Track:** Shared (cross-cutting)

See also:
- `docs/188-verifier-minimum-viable-path.md` (minimal workflow)
- `docs/177-observer-kit-offline-verification-walkthrough.md` (offline walkthrough)
- `artifacts/templates/witness-profile.md` (witness/verification org profile)
- `artifacts/playbooks/spec-error-response-playbook.md` (if verifiers disagree / tool looks wrong)

**Purpose:** get an independent org to a reliable “digest-first” verification posture for the 24–72h post‑election window.

**This is a template.** Fill in jurisdiction + contacts + dates. Keep it to 1–2 pages.

---

## 1) Audience + constraints

- **Audience:** a small team that can operate under time pressure (e.g., newsroom tech desk, civil society watchdog, campaign analytics).
- **Assumption:** they can run a Python script on a laptop but are not expected to read the full archive.
- **Goal:** publish **replayable** verifier output (not just a press statement).

## 2) Outcomes (what “trained” means)

A trained verifier team can:

1. **Verify a packet offline** and emit a `PacketVerificationReport`.
2. **Verify authenticity of an official statement** by comparing PublicNotice digests across channels/mirrors.
3. **Spot missingness / suppression** via coverage reports and liveness beacons.
4. **Publish a digest-anchored verdict** that others can re-run.

## 3) Minimal training plan (90 minutes)

### Module A — Offline packet verification (45 min)

- Get the observer kit (`observer-kit/`) onto an air‑gapped laptop.
- Run the verifier MVP workflow (`docs/188`, `docs/177`) on:
  - a known-good example packet,
  - a packet with an intentionally broken hash.

**Competence check:** the team can explain (in plain language) what “manifest verified” establishes and what it does *not* establish.

### Module B — Digest-first comms verification (30 min)

- Practice verifying one PublicNotice:
  - locate the official digest card / notice,
  - compare with at least one mirror,
  - identify the effective-state pointer if corrections exist.

**Competence check:** the team can produce a “minimum shareable proof” (digest + where it was observed + timestamp window).

### Module C — Human-layer pressure drill (15 min)

Run one drill scenario under time pressure:
- conflicting reports / overload, or
- forged official statement (time-to-refute).

**Competence check:** the team publishes an uncertainty-safe update that commits a `next_update_at`.

## 4) Pre‑election readiness checklist (what must be done before polls close)

- Capacity roster entry exists (`hfv.verifier.capacity_roster`) with:
  - named people on-call,
  - where reports will be published,
  - tool hashes/build info for reproducibility.
- At least one rehearsal produced a public, replayable verifier report (`docs/193`).
- A distribution path exists for “digest-first” verdicts if platforms are unstable (print/QR/digest cards).

## 5) What the team should publish (minimum)

- A replayable `PacketVerificationReport` for each major public packet used in disputes.
- A short “how to reproduce” note (one paragraph) that points to the packet digest and the verifier workflow.
- If there is disagreement: publish it. Silence is not evidence.

## 6) Boundaries (honesty)

- This curriculum does **not** make the team an expert in election law or cryptography.
- It makes them competent to produce **checkable** statements under uncertainty.
- If the team cannot publish replayable outputs, they are not functioning as an independent verifier.
