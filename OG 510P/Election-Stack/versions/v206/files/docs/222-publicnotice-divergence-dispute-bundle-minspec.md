# 222 — PublicNotice divergence dispute bundle minspec (parity failure handoff)

**Track:** A (Deployable core)

When monitors detect that official channels **do not converge** on the same PublicNotice “effective current state” (`220`, `221`), you need a way to turn:

- “audiences saw different official states”

into a **portable, offline-verifiable dispute artifact** that does *not* rely on screenshots, private logs, or trust-me narratives.

This doc defines a **minimal handoff bundle** for PublicNotice divergence / parity failures.

Related:
- PublicNotice as canonical comms artifact: `186`
- Bounded discovery feeds: `200`
- Parity snapshots (portable split-view evidence): `201`
- Request-context variant probing (UA/lang/cache/geo): `224`
- Redaction logs for transformed exhibits (hashes-first): `225`
- Effective-state semantics: `220`
- Monitoring + convergence loop: `221`
- Claim cards + epistemic tags: `217` + `218`
- Court bundle principles: `211`


## 222.1 The claim boundary (keep it small)

A divergence bundle is **not** “the election is compromised.”
It is a bounded claim of the form:

> *“At time T, official channel set S served non-convergent PublicNotice state for subject X (outside holdback window W), and here is the minimum evidence needed to independently verify that statement.”*

Ship a **claim card** (`217`) as `claim.md` and explicitly cite your boundary docs (`166`/`167`).


## 222.2 Minimum evidence objects (MUST vs SHOULD)

This is the smallest set that makes the dispute legible offline.

### MUST

- **At least one `hfv.public.surface_parity_snapshot`** capturing the divergent observations (`201`).
  - Prefer ≥2 independent vantages when possible.
  - If the divergence is specifically about computed “current state” per `220`, begin `observations[].notes` with:
    - `surface_effective_state_divergence` (registry: `docs/SURFACE_ANOMALY_CODES.md`).
  - Each divergent observation MUST carry a **bounded request-context line** (UA class / language / cache-bypass attempt / cookie presence; optional geo/ASN/resolver hints) per `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`.
    - Prefer the canonical compact form: `req[...] vary[...] age[...]` (224.2a) in `observations[].notes` or in `capture-note.md`.

- **The relevant `hfv.public.notice_feed` envelope(s)** (or a bounded feed window) for each official channel that participated (`200`).
  - The bundle MUST include enough feed linkage to prove what each channel pointed at.

- **The referenced `hfv.public.notice` envelope(s)** (and any attached corrections / supersessions needed to compute effective state) (`186`, `220`).

- **A bounded public narrative** as a PublicNotice (yes, another one):
  - publish an incident notice that cites the **snapshot digest(s)** and commits to next update (`186`, `219`).

- **A verification artifact** that makes the packet auditable:
  - `hfv.verifier.packet_verification_report` for the bundle (or for the primary packet if you ship multiple packets) (`193`).

### SHOULD

- **`hfv.governance.official_channel_directory`** (or the most recent directory packet) so a third party can verify the channel set was “official” (`203`, `204`).

- **`hfv.coverage.liveness_beacon`** entries covering the disputed surfaces (freshness headers, reachability) (`210`, `205`).

- **`hfv.time.beacon`** (or a bounded time proof attachment) if the claim is likely to hinge on wall-clock time (`192`).

- A small `capture-note.md` for any raw HTTP captures retained for the dispute (template: `TEMPLATE:artifacts/templates/public-surface-capture-note.md`; quickcheck: `CHECK:artifacts/checklists/public-surface-capture-note-quickcheck.md`; spec: `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`; request-context: `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`).

- `redaction-log.md` if any evidence-relevant exhibit was redacted/transformed for publication (template: `TEMPLATE:artifacts/templates/redaction-log.md`; quickcheck: `CHECK:artifacts/checklists/redaction-log-quickcheck.md`; spec: `DOC:docs/225-redaction-logs-and-transformation-accountability.md`).

- A **public fingerprint report** (`public-fingerprint.json`) for easy mirror/third-party equality checks:
  - preferred (stable file output): `python3 tools/public_fingerprint_report.py <packet_dir> --write-default --stable`
  - or one-command: `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --public-fingerprint --public-fingerprint-out public-fingerprint.json --public-fingerprint-stable`
  - verify (reviewer): `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --verify-public-fingerprint`
  - This is digest-only (no bodies) and is intended to be publishable.

- A verifier report packet (`hfv.verifier.report`) if you have a public verifier surface (`188`, `193`).


## 222.3 Minimal assembly recipe (tight)

1) **Freeze the time window**
   - record `observed_at` for snapshots and the holdback policy you applied (`221.4`).
   - if wall-clock timing is disputed, include a small time proof (e.g., `hfv.time.beacon` or RFC3161 token) per `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md`.

2) **Capture the split-view proof (hashes-first)**
   - build `PublicSurfaceParitySnapshot` for the disputed surface(s):
     - typically `public_notice_feed_latest` and any user-facing status surface (`201`, `195`).

   - If you retained raw HTTP captures to defend the snapshot computation, include a small `capture-note.md` per `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md` (do not ship screenshots).
   - If you publish any cropped/blurred/excerpted exhibit to make the dispute legible, include `redaction-log.md` so the edit is auditable by digest (`DOC:docs/225-redaction-logs-and-transformation-accountability.md`).

3) **Collect what the surfaces *pointed at***
   - include the feed envelopes and the notice envelopes they reference (`200`).

4) **Compute effective state (deterministically)**
   - compute heads + corrections using `220`.
   - record the resulting “effective state set” in the claim card (bounded list of `(notice_id, sha256)` pairs).

5) **Publish an incident PublicNotice**
   - cite snapshot digest(s), state what is known/unknown, commit to next update (`219`).

6) **Package as a bounded offline-verifiable bundle**
   - use the canonical packet layout (`173`) and keep attachments minimal.
   - run `tools/observer_verify_packet.py` and ship the resulting packet verification report (`193`).
   - for publishable packets, also run the conservative hygiene firewall:
     - one-command: `python3 tools/observer_verify_packet.py <packet_dir> --lint-public`
     - or separate: `python3 tools/public_artifact_lint.py --packet <packet_dir>`
   - (recommended) generate a digest-only **public fingerprint** for mirroring/comparison:
     - `python3 tools/public_fingerprint_report.py <packet_dir> --write-default --stable`
   - (reviewer) verify the shipped fingerprint file matches packet bytes:
     - `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --verify-public-fingerprint`


## 222.4 Failure modes this bundle prevents

- **“It worked for me” gaslighting:** one audience’s view is treated as canonical without proving parity.
- **Quiet rollback:** a channel rewrites a feed head; the bundle preserves what was served (`200`, `201`).
- **Interpretation drift:** later narrators widen the claim beyond “divergent state observed” (`217`, `218`).
- **Screenshot theater:** unverifiable images substitute for digest-verifiable artifacts (`180`, `201`).


## 222.5 Size discipline (do not bloat)

- Prefer **hashes + envelopes + receipts** over raw HTML/JSON bodies.
- If a full body is crucial, attach it once as a detached object and reference it by digest.
- Keep the claim card to one page.