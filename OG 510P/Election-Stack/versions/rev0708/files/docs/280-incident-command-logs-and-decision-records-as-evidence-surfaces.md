# 280 — Incident command logs & decision records as evidence surfaces (digest‑first)

**Track:** Shared

This doc fills a narrow gap between:
- `277` (observability + anomaly response surfaces)
- `279` (audit-log digests and tamper-evident journals)
- `259` (incident reporting and coordinated disclosure)
- `186` + `195` + `219` (public incident communications as signed, supersedable notices)

**Problem:** in contested elections, the most damaging disputes often become: *“who decided what, when, and based on what evidence?”*.

Typical incident response already maintains internal logs (tickets, chat, call notes). But those artifacts are:
- operationally noisy,
- rich in sensitive detail,
- hard to authenticate later,
- and easy to selectively leak.

This doc defines a **minimal, publishable evidence surface**: a digest-first, privacy-safe **Incident Command Log Digest (ICLD)** that proves *existence and ordering* of decision records without publishing raw internal logs.

Primary anchors (informative): `source: nist_sp800_61r3_pdf` (incident response lifecycle), `source: nist_sp800_86_pdf` (forensics-in-IR), `source: nist_sp800_92_pdf` (log management), `source: eac_incident_response_comms_guide_pdf` (public comms discipline).

---

## 280.1 The evidence surface

An ICLD is a bounded publishable object that contains:
- a scope (jurisdiction/election_id/incident_id),
- a time window,
- a list of **decision record digests** (and optional event record digests),
- a minimal classification label per record (what kind of decision, not the details),
- and optional proof attachments (timestamp, transparency-log receipt, etc.).
### Canonical template

Use the HFV template:
- `artifacts/templates/hfv.incident_command_log_digest.v1.json`

This is intentionally *digest-first*: publish hashes + minimal labels, keep raw internal logs/tickets sealed unless a controlled-disclosure path is triggered (`278`).


It is **not** the internal log.

Think of it as the public, tamper-evident *table of contents* for the internal log.

### What it buys you

1) **Anti-retcon:** decisions cannot be quietly added, removed, or re-ordered after the fact (assuming regular publication and receipt profiles).

2) **Anti-selective leak:** when parts of the internal log leak, outside parties can verify whether leaked snippets correspond to a committed digest.

3) **Controlled disclosure path:** when litigation, oversight, or a court requires deeper inspection, the ICLD provides a claim-first map for targeted production (pairs with `278`).

---

## 280.2 Minimal record types

Keep the taxonomy tiny. Prefer a single `record_kind` string.

Recommended `record_kind` values:
- `decision`: a decision made by incident command (scope change, containment action, comms posture, escalation).
- `assessment`: a short internal assessment that influenced a decision (e.g., “symptoms consistent with X; confidence Y”).
- `evidence_link`: a pointer (by digest) to an evidence packet or audit-log digest that was considered (`277`, `279`).
- `comms_release`: a pointer to a `PublicNotice` digest that was issued as a result (`186`, `195`).

Avoid adding more unless you can prove it reduces ambiguity without increasing bloat.

---

## 280.3 Publishable shape

### A. Incident Decision Record (internal, but hashable)

An internal record SHOULD be representable as a small canonical text or JSON blob so it can be hashed:
- `record_id` (stable)
- `record_kind`
- `recorded_at` (UTC)
- `roles_present` (coarse roles, not names)
- `decision_summary` (one sentence; avoid sensitive details)
- `rationale_tokens` (hashes of supporting evidence surfaces or assessments)
- `followups` (ticket IDs or internal handles; optionally salted)

The raw record stays internal.
Only its digest and a minimal label appear in the ICLD.

### B. Incident Command Log Digest (publishable)

Template: `artifacts/templates/hfv.incident_command_log_digest.v1.json`.

The ICLD contains:
- `incident_id`, `election_id`, `jurisdiction_id`
- `window_start`, `window_end`
- `publisher` (org + key id, consistent with PublicNotice signing identity; see `208`)
- `records[]`: `{ record_kind, record_id, digest, recorded_at, tags[] }`
- `continuity`: optional `prev_icld_digest` for chaining (hash-chain of digests)

**Publication cadence:**
- during a live incident: publish at a fixed cadence (e.g., hourly) or when a major decision is made.
- after stabilization: publish a final ICLD window that closes the incident.

Bind the ICLD to:
- timestamping (`192` / `265`), and
- optional commitments/log receipts (`261`).

---

## 280.4 Controlled disclosure escalation

The ICLD is designed to support escalation without doxxing staff or exposing sensitive security details.

Escalation ladder:
1. **Public:** ICLD windows + associated `PublicNotice` digests (what was said publicly).
2. **Oversight / bipartisan observers (bounded):** selected decision records corresponding to disputed public claims, with redaction discipline.
3. **Court / litigation:** targeted production mapped from disputed claim → ICLD record(s) → supporting evidence surfaces, using hold/preservation workflow (`278`) and forensics discipline (`source: nist_sp800_86_pdf`).

Rule: do **not** publish raw internal chat logs.
If compelled to disclose, do so via targeted record production with chain-of-custody controls.

---

## 280.5 Stop conditions (anti-weaponization)

Do not publish an ICLD if it would materially:
- expose specific protective posture, vulnerabilities, or access patterns,
- identify staff or enable targeted harassment,
- or leak sensitive operational timing that could enable interference.

If you must pause publication, issue a `PublicNotice` that states the pause and the plan to resume, and commit to the *existence* of withheld windows via a placeholder digest (commitment without details) (`261`, `219`).

---

## 280.6 How this composes with the rest of the Stack

- `277` produces *symptom/evidence digests* (metrics, alert ledgers, outage capsules).
- `279` produces *system journal digests* (audit-log digest commitments).
- `280` produces *decision-order digests* (what incident command decided, and when).
- `186/195/219` produce *public statement digests* (what the public was told and how it was corrected).
- `278/211` provide the path from disputes → preserved evidence → court-ready bundles.

This closes a common narrative gap: “the logs say X” becomes “we committed to X at time T, and you can verify the commitment chain.”


## Optional: transparency-log anchoring

If you need public or multi-party auditability of *when* a digest existed, anchor the digest hash to an append-only transparency log and record the handle in the HFV `transparency_log` block (see `284`). Keep inclusion proofs in a Disclosure Packet (`282`) unless governance requires public release.
