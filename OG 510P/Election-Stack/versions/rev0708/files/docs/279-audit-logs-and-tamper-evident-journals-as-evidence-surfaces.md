# 279 — Audit logs and tamper‑evident journals as evidence surfaces (digest‑first)

**Track:** Shared

Audit logs are often the *first* thing demanded in disputes and investigations — and the *first* thing adversaries try to erase, spoof, or drown. This document defines a **digest‑first** way to treat audit logs as an evidence surface without publishing sensitive raw logs.

This composes with:
- **Proof packaging (CPP):** `docs/265`
- **Time attestation:** `docs/192`
- **Incident disclosure:** `docs/259`
- **Observability/anomaly digests:** `docs/277`
- **Comms + custody posture:** `docs/247`
- **Preservation/hold protocol:** `docs/278`

## 279.1 Threat model (bounded)

We target these failure modes:

1. **Silent tampering:** logs modified or deleted without leaving a verifiable trace.
2. **Split‑view / selective disclosure:** one audience sees “clean” logs; another sees “dirty” logs.
3. **Flooding / obscuring:** huge log volumes used to hide key events.
4. **Time ambiguity:** wall‑clock uncertainty enables disputing event order.
5. **Over‑disclosure:** raw logs leak voter PII, security internals, staff names, or actionable system details.

We do **not** attempt to publish a full logging program; instead we publish **commitments** and **bounded summaries** that enable independent verification and later controlled disclosure.

## 279.2 Minimal publishable surface: Audit Log Digest (AuLD)

Publish **one digest per log system per period** (e.g., daily during pre‑election + election week; weekly otherwise), plus incident‑scoped digests.

**AuLD MUST include (digest‑first):**

- `scope` (system class + environment label; no hostnames)
- `period` (start/end in UTC)
- `event_class_counts` (counts by coarse category; no per‑user rows)
- `collection_posture` (agent type; forwarding path class; time‑sync posture)
- `integrity_commitment` (hash chain / Merkle root / sealed segment digests)
- `seal` (signature digest; optional RFC3161 token digest or other time proof)
- `retention` (policy label + whether under hold, per `docs/278`)
- `access_posture` (role classes; approval path; logging about access)

**AuLD MUST NOT include:**

- per‑voter identifiers, signatures, addresses, DOBs, registration ids
- per‑staff names, personal emails/phones
- precise hostnames, internal IPs, device serials, or exploit‑useful version strings
- raw request bodies, authentication tokens, cookie values

**Source anchors:** NIST guidance on log management and control expectations (informative): `source: nist_sp800_92_pdf`, `source: nist_sp800_53r5_pdf`.

## 279.3 Tamper evidence patterns (choose 1–2; keep it simple)

Use a small number of patterns consistently:

1. **Hash‑chained segments**: compute `H_i = sha256(H_{i-1} || segment_digest_i)` over canonicalized segments; publish the final chain head as the period commitment.
2. **Merkle root per period**: build a Merkle tree over segment digests; publish root + tree size.
3. **Append‑only transparency log (optional)**: publish AuLD commitments (not raw logs) into a public transparency log or witness gossip mesh (`docs/04`, `docs/23`, `docs/261`).

Then apply CPP (`docs/265`) to package the commitment:

- canonicalize → hash → sign → (optional) timestamp → (optional) transparency log entry.

## 279.4 Time discipline (don’t fight about clocks)

For audit evidence, treat timestamps as **claims** that require posture:

- Prefer **monotonic ordering** within a system; treat wall‑clock as informational.
- If order matters externally, attach a **time proof** to the period commitment (e.g., RFC3161 token over the AuLD body hash) per `docs/192`.
- When time sync is degraded, AuLD MUST include a `time_sync_degraded = true` flag and a brief reason code.

## 279.5 When a dispute starts: escalation without dumping logs

When a dispute/incident begins:

1. Publish an **Incident AuLD** for the affected systems for the disputed window.
2. Publish a **controlled disclosure statement**: who can request fuller logs, under what authority, and what redactions will be applied.
3. If litigation hold triggers, emit the minimal **public hold notice** (optional) and record hold status inside AuLD (`docs/278`).

If a court/authorized investigator later requires raw logs:

- produce them as a **sealed disclosure bundle** (CPP + custody chain), not a pastebin.

## 279.6 Operator checklist (tight)

- [ ] Logging scope defined per system class (public web, registration, EPB sync, tabulation, EMS, etc.).
- [ ] Canonicalization and segmentation rule fixed.
- [ ] Periodic AuLD emitted on schedule and signed.
- [ ] Optional time proof attached for externally disputed windows.
- [ ] Access to raw logs is logged (meta‑audit).
- [ ] Retention policy label included; hold status reflected.
- [ ] AuLD commitments are independently witnessed (gossip/transparency) when feasible.



## Optional: transparency-log anchoring

If you need public or multi-party auditability of *when* a digest existed, anchor the digest hash to an append-only transparency log and record the handle in the HFV `transparency_log` block (see `284`). Keep inclusion proofs in a Disclosure Packet (`282`) unless governance requires public release.
