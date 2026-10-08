# 281 — Digest‑first evidence surface kit (AuLD / ICLD / HoldCapsule)

**Track:** Shared

This doc is a *small glue layer* for `277–280`. It standardizes a **digest‑first** pattern you can deploy quickly, without publishing raw internal logs or creating new high‑risk data releases.

It introduces a minimal “kit” of three surfaces:

- **AuLD** — *Audit Log Digest* (`279`) for high‑volume system logs
- **ICLD** — *Incident Command Log Digest* (`280`) for decisions + rationale
- **HoldCapsule** — *Litigation Hold Capsule* (`278`) for preservation + retention overrides

> Goal: when disputes arise, you can prove **existence, ordering, and scope** of records (“what existed, when”) while keeping **raw content controlled** and discloseable only through a governed process.

---

## The kit in one page

### 1) Always publish *digests first*
A digest surface should be sufficient to answer:
- *Did a record exist by time T?*
- *Was the record later altered or re‑ordered?*
- *What scope of systems / teams / vendors is covered?*
- *Where is the authoritative retained copy, and under what policy?*

**Do not publish**:
- raw logs, chat transcripts, ticket bodies, or unredacted attachments,
- PII / voter data, credentials, endpoints, or internal topology,
- vendor identifiers that enable targeted harassment unless already public.

### 2) One canonical header schema (HFV)
All three surfaces should share a small set of header fields:

- `surface_type` (`audit_log_digest` | `incident_command_log_digest` | `litigation_hold_capsule`)
- `surface_version` (semantic, e.g. `v1`)
- `election_context` (jurisdiction, election_id, contest scope)
- `coverage_window` (start/end, timezone)
- `custody` (author, approver, org, retention owner)
- `integrity` (hash algorithm, hash‑chain / Merkle root fields)
- `references` (pointers to sealed raw artifacts; never inline)

**Templates (canonical):**
- `artifacts/templates/hfv.audit_log_digest.v1.json`
- `artifacts/templates/hfv.incident_command_log_digest.v1.json`
- *(Optional)* `artifacts/templates/hfv.signed_digest_statement.v1.json` — sign surface digests and optionally attach receipts (`285`).
- *(Optional)* `artifacts/templates/hfv.timestamp_receipt.v1.json` — external time receipts for digests (RFC 3161 / witnesses) (`287`).

HoldCapsule intentionally remains small and policy‑first; model it as a HFV header + “scope planes” + “retention overrides” as described in `278`.

### 3) A single escalation rule: “digest → disclosure”
A digest is the public (or broadly shareable) surface.
Raw artifacts only leave controlled storage when an escalation threshold is met:

- **Internal review** (Ops + Counsel): verify chain + scope completeness
- **Coordinated disclosure** (per `259`): decide what can be released, to whom
- **Public notice** (per `186/195/219`): issue signed, supersedable updates

This prevents *selective leaks* from becoming the de facto record.

---

## How to deploy in 48 hours (minimal)

1. **Pick a retention owner** (one accountable role) and a signing key policy (`63`, `65`, `73`).
2. **Emit AuLD daily** (or per incident): hash‑chain entries and publish only digests (`279`).
3. **Emit ICLD per incident shift**: record decision IDs + evidence references; publish digest (`280`).
4. **If litigation risk triggers**: create HoldCapsule with scope planes and vendor custody map (`278`).
5. **Bind to public comms**: every public incident update links to the relevant digest IDs (`186/195/219`).

---

## Minimal interoperability rules (to avoid tool lock‑in)

- Treat *all pointers* as URIs (could be S3, GCS, SharePoint, local vault IDs).
- Allow multiple signers (county + state + vendor) but require **one canonical digest** per surface per coverage window.
- Prefer stable identifiers:
  - `digest_id` = `YYYYMMDD` + jurisdiction + surface_type + short hash prefix
  - `record_id` = monotonic within the coverage window

---

## Failure modes this kit prevents

- **Retconning:** later rewriting “what we did” without leaving trace (`279/280`).
- **Disclosure panic:** publishing raw logs because there is no safer alternative (`259`).
- **Custody fog:** unclear who held what and under which retention authority (`278`).
- **Harassment via leakage:** exposing internals or vendor staff identifiers unnecessarily (`22/39/225`).

---

## Cross‑links

- Observability & anomaly response surfaces: `277`
- Litigation hold & preservation: `278`
- Audit log digest & tamper‑evidence: `279`
- Incident command decision digests: `280`


- Transparency-log anchoring for digests (optional): `284`
- Timestamp receipts for digest evidence (optional): `287`

---

## Optional: anchor digests to a transparency log

If you need cross-organization verification that a digest existed at (or before) a time, anchor the **digest hash** (not raw logs) to an append-only transparency log, and record the returned handle in the HFV `transparency_log` block. Keep proofs in a controlled-disclosure layer (`282`) unless your governance explicitly authorizes public release.

See: `284`.
