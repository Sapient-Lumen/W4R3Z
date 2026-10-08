# 192 — Time attestation & timestamping as evidence

**Track:** Shared

Time is a common failure mode for election systems:
- clocks can be **shifted** (on‑path NTP attacks, misconfiguration),
- clocks can **diverge** across jurisdictions (forked timelines),
- and “what happened first?” disputes can turn into litigation.

This archive already treats **log order** as canonical (`docs/31`, `docs/38`).
This doc adds a tight, evidence‑packaging view:

- how to harden operational time sync,
- how to produce **portable** time attestations,
- and how to bind “this evidence existed by time T” without inflating the archive.

## 192.1 Non-negotiable premise: ordering ≠ wall-clock

- **Canonical order** MUST come from the transparency log / checkpoints.
- Wall‑clock time is for:
  - coarse UI boundaries,
  - deadline semantics that are themselves *evidence‑anchored* (trigger events + publication contracts),
  - and forensic reconstruction.

If a claim needs time to be correct, it needs a **time proof**.

## 192.2 Operational time sync (protect the clock)

### Prefer NTS‑secured NTP (when you control the fleet)

NTP by itself is widely deployed but historically unauthenticated (`source: rfc5905_txt`).
When possible, use **Network Time Security (NTS)** to authenticate time synchronization (`source: rfc8915_txt`).

Operational guidance (tight):
- Use **multiple** independent servers (different operators / networks).
- Treat time as an *interval* (min/max plausible window), not a point.
- Persist a monotonic “last known good” window; refuse large jumps without operator‑visible alarms.

### Use Roughtime for rough-time bootstrapping + misbehavior proofs

Roughtime is designed to provide authenticated rough time **and** a format for proving server inconsistency (`source: draft_ietf_ntp_roughtime_17_txt`).

Recommended posture:
- Query multiple independent servers.
- Store the query/response transcripts as evidence objects (see §192.4).
- Treat Roughtime as *rough* by construction; it’s for safety and dispute resistance, not sub‑second sequencing.

### Log-management tie-in

When time is part of operational evidence, log management must explicitly address clock synchronization assumptions and failure modes (`source: nist_sp800_92r1_ipd_pdf`).

## 192.3 “Existence-by-time” proofs (timestamping)

Sometimes you need to show:
> “This exact artifact existed no later than time T.”

A common approach is using a Time Stamping Authority (TSA) and the Time‑Stamp Protocol (`source: rfc3161_txt`).

This archive does **not** mandate a TSA ecosystem, but provides a packaging pattern:

- Compute a digest you want to time‑bind (usually `EvidenceEnvelope.tbs_digest` or `payload_digest`).
- Obtain a TSA time‑stamp token over that digest.
- Ship the token as a small detached attachment.

This keeps the archive small (token bytes, not third‑party PDFs).

## 192.4 Packaging time proofs in EvidencePackets (no new schema required)

Use standard packet objects + attachments:

Complementary pattern (local attestation): publish periodic `hfv.time.beacon` envelopes whose payload is `schemas/TimeBeacon.json`. The **EvidenceEnvelope signature** provides authenticity; the payload SHOULD describe the time source + uncertainty and MAY reference attached time-proof objects by digest.

- Place the proof bytes under `objects/` with a content‑addressed name:
  - `objects/sha256-<hex>.tst` (RFC3161 token)
  - `objects/sha256-<hex>.roughtime` (Roughtime transcript or canonical JSON wrapper)

- Include them as `attachments[]` in the relevant `EvidenceEnvelope`.

- In the envelope `subject`, describe what is being time‑bound:
  - `"time_binds": "tbs_digest"` or `"time_binds": "payload_digest"` (as a human-readable convention; do not rely on it mechanically).

Verifier minimum behavior:
- Verify the envelope’s `payload_digest` and `tbs_digest` first.
- Treat time proofs as **supporting evidence** that constrain plausible timelines.
- Prefer policies that accept **multiple** independent proofs rather than single points of failure.

## 192.5 Policy hooks (where time proofs actually matter)

Time proofs become operationally meaningful when paired with:

- publication contracts and trigger events (`docs/181`, `docs/184`),
- suppression / deadline breach reports (`docs/181`, `docs/187`),
- incident communications that must be anchored to a timeline (`docs/186`).

Do not accept “the system said it was 8pm” as evidence.
Accept: “here are the signed triggers, checkpoints, and time‑proof objects that bound the timeline.”

## 192.6 Practical constraint: access-restricted guidance

Some operational time-resilience guidance is published behind access controls or rate limits; if you cite it, record it in the lockfile as best‑effort unpinned (`xref: cisa_time_guidance_network_operators_2023_pdf`).

