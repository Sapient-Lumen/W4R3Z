# 240 — Deepfake frontier + time-to-refute discipline (public-surface authenticity in the AI era)

**Track:** A (Deployable core)

Synthetic media and impersonation attacks are moving faster than any static specification.
This archive therefore does **not** try to “solve deepfakes.”
Instead, it defines a **verifiable public-surface posture** that makes rapid refutation and split-view detection *possible*.

This doc is a compact bridge between:
- synthetic-media minimum controls (`194`),
- PublicNotice as evidence (`186`) + status-board pattern (`195`),
- epistemic-tagging and update commitments (`218–219`),
- discovery + mirroring (`200–205`),
- key lifecycle discipline (`239`),
- witness ecosystems as countervailing power (`135`),
- publication compliance + “minimal adversarial publication test” (`187`).

## 240.1 The threat (what changes in the AI era)

A modern election disinformation attack can be:
- **high velocity**: fabricated “official” audio/video or screenshots circulate before any official clarification exists,
- **split-view**: different audiences see different “official” statements (or different versions of the same page),
- **trust hijack**: attackers impersonate trusted individuals, not just institutions.

The failure mode is not only “a fake exists.” It is **time-to-refute** and **time-to-consensus**.

## 240.2 What the archive *does* claim (and what it does not)

**Claim (A):** A jurisdiction can make its official communications and incident updates *cryptographically checkable*
by publishing digest-first PublicNotices and mirrorable discovery pointers.

**Claim (B):** Operators can measurably reduce rumor vacuum and overclaim by using epistemic tags and explicit update commitments.

**Non-claim:** The archive does not claim to detect deepfakes reliably, to attribute authorship of viral media,
or to prevent coercion/social manipulation via comms channels.

## 240.3 Time-to-refute (TTR) as a measurable operational budget
Treat **TTR** as a requirement, not a vibe.

Define two clocks (so drills don’t “pass” on technicalities):

- **TTR‑1 (thin refutation):** time from first internal recognition of a high-impact false claim → a signed PublicNotice exists and is mirrorable.
- **TTR‑2 (thick refutation):** time from first internal recognition → an evidence packet exists that a third party can verify offline (notice chain + receipts + any verifier reports).

Recommended initial targets (adjust to staffing reality, but publish *something*):
- TTR‑1 ≤ **10–15 minutes**
- TTR‑2 ≤ **60 minutes** (often faster if tooling is rehearsed)

Record TTR‑1/TTR‑2 for drills and incidents and keep the result auditable via the bounded registry (`artifacts/registries/time-to-refute-evaluations.csv`).

### Roles, tools, and communication pathway (minimum)

1. **Authenticity response cell** (small, on-call): has signing access, can run the offline verifier, and can publish a PublicNotice + packet.
2. **Comms lead** (publisher): drafts the human-facing text but does not get to ship unverifiable claims.
3. **Mirror operators**: replicate the notice/packet quickly across independent distribution paths (`200–205`, `106`).
4. **Independent verifiers / witnesses**: re-run the verifier and publish replayable output (PacketVerificationReport, cosigns, or dissent) (`188`, `135`).
5. **Monitoring cell**: runs MAPT checks to confirm the refutation is observable from multiple perspectives (`187`).

Pre‑positioning note (so these targets are real): publish a verifier capacity roster **before polls close** (who will verify + where replayable reports land). If no independent verifier capacity is visible, TTR targets are fantasy.
See: `241` (kind `hfv.verifier.capacity_roster`).


### Drill artifacts (keep them compact)

- Test plan template: `artifacts/templates/time-to-refute-test-plan.md`
- Refutation packet checklist: `artifacts/checklists/time-to-refute-refutation-packet-checklist.md`
- On-call checklist: `artifacts/checklists/authenticity-response-cell-checklist.md`
- Log measured outcomes (bounded refs only): `artifacts/registries/time-to-refute-evaluations.csv`

Suggested drill artifact:
- use the operator cell checklist (`artifacts/checklists/authenticity-response-cell-checklist.md`) and publish an example notice chain.

## 240.4 The “refutation packet” (minimum publishable shape)

When a high-impact false claim is circulating, the refutation should be publishable as:

1) **PublicNotice** (digest-first; signed; mirrored) with:
   - epistemic tags + confidence on load-bearing sentences (`218–219`),
   - explicit “next update by” commitment when uncertainty remains (`219`),
   - links forward/backward in the notice graph (`220`).

2) **Discovery pointers** that make the authoritative bytes easy to find (`200–205`):
   - `.well-known` pointer(s),
   - feed + mirror index entries,
   - stable directory listing.

3) **Keyset anchoring** to keep “official voice” legible during key rotation / compromise (`239`).

4) **Optional witness cosigns / dissent** when institutional trust is contested (`135`):
   - cosign the notice digest or publish a counter-notice that cites it.

This is intentionally “boring”: the goal is not persuasion by style; it is **verification by anyone**.

## 240.5 Failure signals (when you are losing)

- Refutations require a press call to “trust us” (no checkable object exists).
- Official surfaces are not mirrorable/compareable (single points of failure; dynamic apps; unstable links).
- The “current statement” is ambiguous (no correction chain semantics; no effective-state policy).
- Witnesses are silent, monoculture, or cannot publish independent notes.

If these occur, treat it as an incident on the comms/authenticity surface (`186–187`, `195`), not “PR trouble.”

