# 195 — Rumor control & status boards as verifiable public surfaces

**Track:** A (Deployable core)

This doc is a **tight operator pattern** that connects:
- `186-incident-communications-as-evidence.md` (PublicNotice as the canonical comms unit)
- `219-uncertainty-safe-public-updates.md` (epistemic tags + update commitments inside notice/statement text)
- `200-publicnotice-feeds-and-mirror-index.md` (bounded discovery + rollback detection for notices)
- `220-publicnotice-graph-resolution-and-effective-state.md` (supersedes/corrections → deterministic “current state”)
- `193-publishable-verifier-reports.md` (publishable verifier output)
- `194-synthetic-media-and-comms-authenticity-minimum-controls.md` (AI-era authenticity controls)
- `240-deepfake-frontier-and-time-to-refute.md` (time-to-refute discipline + refutation packet shape)
- `197-precinct-closeout-evidence-capture-and-publication.md` (poll tape / closeout micro-packets as linkable evidence)
- `198-precinct-closeout-index-and-omission-detection.md` (closeout index for omission detection)

Goal: make “what is the current official state?” **cheap to verify** and **hard to spoof**, without requiring everyone to run a full verifier in the moment.

## 195.1 Principle

A rumor-control page and incident status board are not “content” — they are **verification surfaces**.

They MUST behave like an index over content-addressed `PublicNotice` envelopes:
- the page is *a view*;
- the notice digest is *the authority*.

If you have more than a handful of notices, publish a `PublicNoticeFeed` (docs/200) and render the board from the latest feed rather than from an editable database.

Use `220` to compute the board’s **effective “current state”** from `supersedes_notice_id` and `correction_of_notice_id` (and to treat forks/missing corrections as incidents).

Operationally: your staff writes messages, but your ecosystem verifies **digests + multi-vantage receipts**, not screenshots.

## 195.2 Minimum viable surfaces (Track A)

### 0. PublicNotice feed index (SHOULD)
Publish the latest `hfv.public.notice_feed` (docs/200) at a stable location on each official surface.
The rumor-control/status board SHOULD:
- render entries from the latest feed window, and
- display the feed digest (short form) so viewers can cross-check parity across channels.
- prefer emitting these short digests via bounded **digest cards** (docs/206) to avoid transcription errors across channels.
- link to or display the short digest of the domain-first `/.well-known/election-stack.json` discovery surface (docs/204) alongside the feed digest (helps outsiders bootstrap without trusting editable CMS content).
- display (or link to) the short digest of the latest **PublicNotice signing keyset** (docs/208) so audiences can verify which keys are authorized to sign notices.
- treat the machine-facing feed/directory/well-known pointers as freshness-sensitive; use explicit short-TTL cache controls (docs/205).
- ensure machine-facing pointer surfaces pass **MAPT** (minimal adversarial publication test; `docs/187`) so “technically public” remains operationally usable under incident stress.

When parity is disputed or fails, monitors SHOULD publish a bounded `hfv.public.surface_parity_snapshot` (docs/201) and the comms team SHOULD cite its digest in a PublicNotice.


### A. Rumor-control surface (MUST)
Use `PublicNotice.notice_type = rumor_control` for every “myth → fact → how to verify” correction.
Guidance: CISA “Rumor vs. Reality” posture (informative baseline) (`xref: cisa_rumorcontrol_page`) and operator-facing comms toolkits (`source: eac_enhancing_election_security_public_comms_2024_pdf`, `xref: eac_communicating_election_post_election_toolkit_2026_page`).

**Every rumor-control entry MUST include:**
- the `PublicNotice` digest short form (copy/pasteable),
- a pointer to at least two mirrors/witnesses (anti selective disclosure),
- a “how to verify” section that points to **packet digests + verifier output**, not rhetoric.

### B. Incident status board (MUST)
Use `PublicNotice.notice_type = status_update` for operational state updates.
Follow incident-communications guidance for cadence and clarity (`source: eac_incident_response_comms_guide_pdf`, `xref: cisa_voluntary_incident_reporting_guidance_2024_pdf`), but bind updates to digests.

**Each status update SHOULD include:**
- `issued_at` and **`next_update_at`** (make silence diagnosable),
- scope (jurisdiction + election_id),
- a single-sentence “what changed” summary,
- the digest short form and mirror pointers,
- an optional `references[]` entry pointing to a publishable `PacketVerificationReport` digest (when the update asserts something about evidence).


### B2. Closeout index surface (SHOULD)
If you publish precinct closeout micro-packets (`197`), your public surface SHOULD also publish or reference a **PrecinctCloseoutIndex** (`198`) so selective omission is measurable.

The status board should point to the index digest (or the PublicNotice digest that announces it), not to an editable “list of precincts.”

### B3. Surface security snapshot surface (SHOULD)
If your rumor-control/status board is part of your official comms surface, publish or reference the latest **OfficialSurfaceSecuritySnapshot** (`199`) so the public can see an auditable record of DNS/TLS/email anti-spoofing posture during incidents.

The board SHOULD show the snapshot digest (or the PublicNotice digest that announces it), not a prose claim like “our domain is secure.”

### C. Channel registry + parity (MUST)
Maintain a canonical registry of official comms surfaces (deployment-local analogue of `artifacts/registries/official-channels.csv`).
Observers SHOULD parity-check that the same notice digest appears across declared channels and emit discrepancy evidence when parity breaks (`194`, `104`).

## 195.3 The page format (keep it boring)

The page itself can be HTML, JSON, or both. The invariant is the **entry schema** (human-first; machine-scrapable):

- **Digest:** `<short_digest>` (with a full-digest copy affordance)
- **Type:** `status_update | rumor_control | incident_advisory | correction | election_milestone | ...`
- **Graph:** `supersedes_notice_id` / `correction_of_notice_id` if present (use `220` for resolution)
- **Issued:** `<issued_at>` (UTC recommended)
- **Next update:** `<next_update_at>` or explicit “no further updates expected”
- **Title:** `<title>`
- **Mirrors:** `<mirror_1>`, `<mirror_2>`, …
- **Verify:** pointer to packet/verifier instructions (offline-friendly)

Template (optional, keep it boring): `artifacts/templates/public-status-page.md`.

Do not pack long narrative text into the board. The board points at **notices**; notices can carry structured details and attachments.

## 195.4 Compromise and rollback posture (do not improvise)

If a declared official channel is compromised or suspected compromised:
1. Publish an `incident_declaration` or `incident_advisory` `PublicNotice` stating which channel(s) are affected.
2. Require all other channels to **re-state the digest** of that notice (parity asserts that unaffected channels agree).
3. If you must “take down” a message, publish a `correction` `PublicNotice` that links via `correction_of_notice_id` / `supersedes_notice_id` instead of silently deleting.
4. Use general incident-response best practice for containment and recovery (`source: nist_sp800_61r3_pdf`).

This turns “comms chaos” into an auditable sequence of statements, even under partial compromise.

## 195.5 Verifier-facing hook (optional but powerful)

When a status update depends on evidence (e.g., “packet X is complete” or “manifest matches published digest”):
- link the update to a publishable `PacketVerificationReport` digest (`193`), and
- publish the report packet alongside the notice packet (same mirrors).

This lets third parties cite a short digest rather than re-litigating screenshots and hearsay.
## 195.6 Minimum deployable checklist (Track A, size-disciplined)

This is the **smallest set of publishable surfaces** that makes “what is the official state?” cheap to verify under distortion.
Prefer digests + indexes over prose.

| Item | What you publish | Where it lives | Why it matters |
|---|---|---|---|
| Domain-first bootstrap | `/.well-known/election-stack.json` digest (`204`) | jurisdiction domain | Lets outsiders bootstrap without trusting editable CMS pages. |
| Official channel directory | latest `OfficialChannelDirectory` digest (`203`) | at least 2 channels | Defines the authoritative set of channels to parity-check. |
| Signing keys allow-list | latest PublicNotice signing keyset digest (`208`) | alongside the directory | Makes forged “official notices” cheaper to falsify. |
| Notice feed window | latest `PublicNoticeFeed` digest (`200`) | every official surface | Prevents “latest pointer” split-views; supports mirror comparisons. |
| Rumor-control entries | `PublicNotice` digests (`186`) + verify pointers | rumor-control page (`A`) | Turns “myth → fact” into auditable objects, not screenshots. |
| Incident status updates | `PublicNotice` digests + `next_update_at` | status board (`B`) | Makes silence diagnosable and rollback auditable. |
| Verifier policy profile | `VerifierPolicyProfile` digest (pinned + shipped) (`188`) | alongside publishable reports | Makes third-party interpretations comparable (thresholds/time rules) without trusting prose. |
| Parity dispute evidence | `PublicSurfaceParitySnapshot` digest (`201`) | published by monitors | Captures split-view as evidence without rehosting content. |
| Surface posture snapshot | `OfficialSurfaceSecuritySnapshot` digest (`199`) | optional but recommended | Anchors DNS/TLS/email anti-spoofing posture during incidents. |

## 195.7 Authenticity verdict lane (time-to-refute)

During the critical post-election window, treat “is this official?” as a first-class status-board lane:
publish **digest-anchored authenticity verdicts** as `PublicNotice` objects and render them as board entries.

Operator checklist: `artifacts/checklists/authenticity-response-cell-checklist.md` (drill this; see the time-to-refute targets in `194.4`).

Operational cautions:
- Keep the surface **digest-first**: publish small digests + machine indexes; do not rehost bulk packets on the board itself.
- Do not publish internal hostnames, file paths, or private infrastructure details; publish only the verifiable public surfaces above.
