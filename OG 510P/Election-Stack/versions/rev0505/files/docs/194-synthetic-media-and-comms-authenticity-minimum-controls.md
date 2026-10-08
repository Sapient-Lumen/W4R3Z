# 194 — Synthetic media & comms authenticity (minimum deployable controls)

**Track:** A (Deployable core)

This doc is a **tight, deployable** supplement to:
- `37-public-evidence-and-disinformation-resilience.md`
- `186-incident-communications-as-evidence.md`
- `195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`

It focuses on a single hard problem: **when fake screenshots and forged “official statements” can be mass-produced, how do we make authenticity cheap to check?**

We assume:
- screenshots are trivial to forge;
- adversaries can post convincing “official” content on hijacked channels;
- many observers will not run full verifiers in the moment.

Track A posture: **don’t promise to eliminate deception**—make deception *measurably harder* and *faster to debunk* using content-addressed evidence.


## 194.1 Design principle

**If a claim matters, bind it to a digest.**

For Track A, the digest-bearing unit is a `PublicNotice` envelope (`hfv.public.notice`), published with:
- an envelope digest (copy/pasteable short form), and
- receipts + gossip attachments (anti selective disclosure), per `180`.

A human should be able to answer, quickly:
- “Is this message byte-identical to what the operator published?”
- “Did multiple mirrors/witnesses see the same digest?”


## 194.2 Minimum control set (Track A)

### A. Content-addressed official statements (MUST)
- Publish all incident-relevant public statements as `hfv.public.notice` evidence envelopes (`186`).
- Every channel surface (web, social, press PDF) SHOULD carry the **notice digest** and a pointer to mirrors.
- Never rely on screenshots as the primary record; screenshots can be attachments *to* a notice, not the notice itself.

### B. Official-channel registry + parity monitoring (MUST)
- Maintain a canonical registry of official comms surfaces (`artifacts/registries/official-channels.csv`).
- Observers SHOULD monitor for **parity** (same notice digest on all declared official channels) and emit a signed discrepancy notice when parity breaks.

### C. Channel hardening baseline (SHOULD)
At minimum (see hardening checklist):
- harden domain/TLS/email controls and monitor for mis-issuance and spoofing (`xref: cisa_bod_18_01_page`, `source: rfc9162_txt`, `source: rfc8659_txt`, `source: rfc7208_txt`, `source: rfc6376_txt`, `source: rfc7489_txt`).
- treat comms-channel credential recovery as a pre-drilled incident scenario (`artifacts/registries/drill-scenarios.csv`).
- publish an **OfficialSurfaceSecuritySnapshot** so the hardening posture is auditable and changes are detectable (`docs/199`).

### D. Correction + rumor-control workflow (MUST)
- Corrections MUST be new notices with explicit linkage (`correction_of_notice_id`), not silent edits (`186`).
- Rumor-control notices MUST prefer “myth → fact → how to verify” and point to reproductions (packet digests + verifier commands), not rhetoric (`xref: cisa_rumorcontrol_page`, `source: eac_enhancing_election_security_public_comms_2024_pdf`).

### E. Media provenance signals (OPTIONAL; never sufficient alone)
Signals like Content Credentials can help some audiences, but are not a substitute for content-addressed evidence:
- If you publish images/video, you MAY attach provenance metadata and cite the standard (`xref: c2pa_content_credentials_spec_2_2_pdf`).
- Treat provenance as **advisory**: verifiers still anchor authenticity via notice digests and receipts.
- Never embed voter identifiers or individualized watermarks in public comms artifacts.

### F. Pre-election public “how to check” guidance (SHOULD)
- Publish a short guide that teaches audiences to validate:
  - the notice digest,
  - the official-channel registry,
  - mirror/receipt corroboration.
- Align with operator-facing comms toolkits when helpful (`xref: eac_communicating_election_post_election_toolkit_2026_page`, `source: eac_ai_toolkit_2023_pdf`).


## 194.3 Minimal deliverable: a comms-authenticity packet

For major incidents, publish a small packet that contains:
- at least one `hfv.public.notice` envelope,
- receipt + gossip attachments (per profile),
- `official-channels.csv` (or a digest pin + pointer),
- any referenced evidence-object digests (availability proofs, publication compliance reports, etc.).

This packet exists to make “what was said, when, and on which channels” **portable evidence**, not a debate.




## 194.4 Time-to-refute (operational model)

Deepfakes matter most in the **first 24–72 hours** after polls close: the adversary’s goal is often not perfect fakery,
but enough doubt that authenticity becomes contested.

Track A posture: pre-position the ability to answer “authentic or not?” **faster than rumor spreads**.


Define two clocks (so drills don’t “pass” on technicalities):

- **TTR‑1 (thin refutation):** first internal recognition → a signed, mirrorable PublicNotice verdict exists.
- **TTR‑2 (thick refutation):** first internal recognition → an offline‑verifiable evidence packet exists (notice chain + receipts + any verifier reports).

(See `docs/240` and `artifacts/checklists/time-to-refute-refutation-packet-checklist.md`.)

Deployments SHOULD define and drill:
- **Who is watching:** a small “authenticity response cell” (operator + at least 2 independent monitors).
- **What they can do quickly:** fetch the disputed artifact, compare against PublicNotice digests and keyset pins, and publish a bounded verdict notice that points to a packet digest.
- **Where the verdict lands:** official status surface + mirrors + low-bandwidth digest card (`195`, `206`).

Pre-positioned prerequisites (so “fast refute” is real):
- have at least one **mirror** and one **independent monitor** running before polls close,
- pre-share a tiny “digest-first” verification workflow with key newsrooms/civil-society partners (who will publish replayable verdicts),
- pre-author an authenticity-verdict PublicNotice template (myth → fact → how to verify) and rehearse the posting path.
- publish a verifier capacity roster (who will look + where replayable verifier reports land) before polls close (`241`; kind `hfv.verifier.capacity_roster`).

**Tooling to pre-position (keep it boring):**
- one-command offline verifier workflow (`observer-kit/`, `177`),
- feed/keyset fetch + digest-short-form helper for comms staff,
- parity snapshot + liveness beacon capture for “split view” reports (`201`, `210`).

**Communication pathway (faster-than-rumor wiring):**
1) authenticity response cell publishes a verdict PublicNotice (or `UNCONFIRMED` with `next_update_at`) and updates the status/rumor-control surface (`195`, `218–219`).
2) independent verifiers named in the capacity roster (`241`) fetch the packet and publish replayable PacketVerificationReports to their report feeds (`188`, `193`).
3) status/rumor-control updates link to those verifier outputs by digest (`references[]`), and mirrors re-publish the digests if official channels degrade (`200–205`).
4) publish a low-bandwidth digest card for high‑reach channels that points back to the status surface and verifier report feeds (`206`).

Suggested starting targets (set locally; then drill):
- forged “official statement” (high severity): publish a digest-anchored authenticity verdict within **≤ 60 minutes**,
- top-level outcome / concession style forgery: **≤ 15 minutes** if feasible (requires pre-positioned monitoring).

If you cannot meet your target, treat that as a capability gap and fix it pre-election.

**Operator artifact:** `artifacts/checklists/authenticity-response-cell-checklist.md` (drillable, bounded).

## 194.5 What this does not solve (explicit non-claims)

- It does not prevent channel takeover.
- It does not guarantee everyone will check digests.
- It does not prove intent.

It makes two narrower things true:
1) the authentic operator statement is cheap to authenticate (byte-level), and
2) selective omission or split-view publication is detectable by third parties.


## Cross-links
- Disinformation resilience overview: `37-public-evidence-and-disinformation-resilience.md`
- Public comms as evidence: `186-incident-communications-as-evidence.md`
- Receipts + gossip: `180-receipts-and-gossip-attachments.md`
- Publication contracts and compliance proofs: `181`, `187`
- Official surface security snapshots: `199-official-surface-security-snapshots.md`
