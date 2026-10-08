# 223 — Public-surface capture notes (reproducibility without bundle bloat)

**Track:** A (Deployable core)

When an incident hinges on **what an official surface served** (feeds, status boards, well-known discovery), the stack prefers **hashes-first** artifacts:

- `PublicSurfaceParitySnapshot` (`DOC:docs/201-public-surface-parity-snapshots.md`)
- `LivenessBeacon` reachability + freshness headers (`DOC:docs/210-liveness-beacons-and-missingness-surface.md`)
- chained discovery/feed semantics (`DOC:docs/200-publicnotice-feeds-and-mirror-index.md`, `DOC:docs/205-cache-and-freshness-controls-for-public-surfaces.md`)

But some disputes (or litigation) require you to retain **raw captures** (HTTP headers + body bytes) so a third party can independently recompute digests and confirm the capture wasn't “hand-transcribed.”

This doc defines a **minimal capture-note convention** that makes raw captures usable and court-explainable **without shipping huge bodies by default**.

Related:
- Evidence pointers for detached bytes: `SCHEMA:schemas/EvidencePointer.json`
- PublicNotice divergence handoff bundle: `DOC:docs/222-publicnotice-divergence-dispute-bundle-minspec.md`
- Redaction discipline: `DOC:docs/189-sensitive-material-and-secrets.md` + `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md` + `DOC:docs/225-redaction-logs-and-transformation-accountability.md`
- Time attestation & timestamping (if wall-clock time is disputed): `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md`
- Request context & variant probing: `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`


## 223.1 Goal

A capture note SHOULD let an independent verifier answer:

- *What was fetched (which surface, which official channel, which URL target)?*
- *When was it fetched (UTC), with what time source, and with what tool / command?*
- *What bytes were captured (digest pins for body bytes and for the capture file itself)?*
- *What context is needed to rebut “you hit a different endpoint” objections (DNS/TLS basics)?*

It MUST stay **small** and **publishable after redaction**.


## 223.2 What to store vs what to publish

**Store (often private / sealed):**
- raw `curl -i` / `wget --server-response` capture bytes (headers + body)

Tooling note: the stdlib capture distillers in `tools/` are tolerant of common capture quirks (redirect chains, proxies, and indented status lines from `wget -S`).
- optional DNS answers / resolver transcript
- optional certificate chain export

**Publish (usually):**
- parity snapshot + liveness beacon + notice/feed envelopes
- capture note with digests that point to the stored raw bytes

Only attach raw bodies publicly when they are truly load-bearing and cannot be reconstructed from other published envelopes.


## 223.3 Minimal capture note format

Ship a single markdown file (recommended name: `capture-note.md`) in the bundle.
Use the template:

- `TEMPLATE:artifacts/templates/public-surface-capture-note.md`

Minimum fields (keep tight):

1) **Subject**
- `surface_kind` + `stable_target` (from `DOC:docs/201-public-surface-parity-snapshots.md`)
- `channel_id` (from `artifacts/registries/official-channels.csv`)
- retrieval location (a URL string or a “channel → URL mapping” reference)

2) **Acquisition metadata**
- `fetched_at` (UTC)
- `time_source` (e.g., `nts_ntp`, `roughtime`, `system_clock`, `unknown`)
- `time_uncertainty` (e.g., `±2s`, `±30s`, `unknown`)
- tool + version (e.g., `curl 8.x`, `wget 1.x`)
- a bounded command line (omit tokens, cookies, auth headers)

3) **Request context (bounded)**
- `ua_class` (coarse: `desktop_chrome`, `mobile_safari`, `cli_curl`, …)
- `accept_language` (e.g., `en-US`, `none`)
- `cache_bypass` (e.g., `none`, `no-cache`)
- `cookies` MUST be `none` for public captures (or `present_redacted` without values)
- optional `geo_hint`/`asn_hint` if publishable
- optional `resolver_hint` (`system_resolver|public_resolver|pinned_resolver`) if it helps classify split views (coarse; names OK; transcripts usually private)
- optional response variance hints: `Vary` / `Age` (bounded; prefer canonical `vary[lowercase,comma,no-spaces] age[int]`)
- optional compact portability note: `req[...]` / `vary[...]` / `age[...]` in canonical form (see `DOC:docs/232-compact-request-context-notes.md` and `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`, 224.2a)

4) **Digest pins (hashes-first)**
- `body_sha256` (digest of response body bytes)
- `capture_file_sha256` (digest of the full capture file, including headers)
- `time_proof_digests` (optional: digests of attached RFC3161 tokens / Roughtime transcripts / time beacons; see `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md`)
- if decompression/transforms happened, note the transformation and pin both digests

5) **Network context (minimal)**
- DNS: either “system resolver” or a short list of resolved IPs (if publishable)
- TLS: server cert SPKI fingerprint (or leaf cert fingerprint) if captured

6) **Redaction notes (if any)**
- what was removed and why (cite `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`); if any published derivative was produced (cropped/blurred/excerpted), include `redaction-log.md` per `DOC:docs/225-redaction-logs-and-transformation-accountability.md`


## 223.4 How capture notes integrate with existing dispute artifacts

### A. Parity snapshots (201)

If a parity snapshot observation is derived from a raw capture:
- keep the snapshot hashes-first,
- and include a short note like `derived_from_capture_note` pointing to the capture note path (not a URL).

### B. Divergence dispute bundles (222)

In a `DOC:docs/222-publicnotice-divergence-dispute-bundle-minspec.md` bundle:
- include the capture note when any party is likely to contest the parity snapshot computation,
- and list the capture-note digests in the `claim.md` “Evidence present” section (`DOC:docs/217-claim-cards-and-traceability-minspec.md`).

### C. EvidencePointer for detachable raw bytes

When you do attach raw captures to the packet:
- store them once,
- reference them with `EvidencePointer` digests (and `media_type: application/octet-stream` or `text/plain`),
- and cite their digests from the capture note and claim card.


## 223.5 Size discipline

- One capture note per disputed surface per time window.
- Do not include full header dumps for every retry; pin one canonical capture and summarize the rest.
- Prefer capturing **the minimal machine-facing JSON** (feeds/discovery) over large HTML pages.


## 223.6 Time pinning (optional but often decisive)

If the dispute is likely to hinge on *when* the bytes were served (not just *what* bytes), treat wall-clock time as **supporting evidence** and pin it:

- record `time_source` and `time_uncertainty` in the capture note;
- when feasible, include a small time proof per `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md` (e.g., an RFC3161 token over `body_sha256` or a contemporaneous `hfv.time.beacon`), and list its digest under `time_proof_digests`.

Do not inflate bundles with third-party time PDFs; ship the token bytes only.
