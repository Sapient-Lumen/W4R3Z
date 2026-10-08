# Integrity drills and rehearsals for digest-first evidence surfaces

**Track:** A (Deployable core)  
**Status:** Proposed / deployable pattern  
**Related:** `docs/279` (AuLD), `docs/280` (ICLD), `docs/281` (kit), `docs/282` (controlled disclosure), `docs/283` (triage tags), `docs/285` (SDS), `docs/287` (timestamp receipts)

This document defines a small, bounded practice: **run short integrity drills** that prove you can produce *digest-first* evidence (and, when required, controlled disclosures) **on demand**, without leaking raw logs by default.

## Why this matters

A well-designed evidence surface is still fragile if nobody rehearses:
- **Can we produce a digest quickly and consistently?**
- **Can we prove who signed it, when, and under which policy?**
- **Can we escalate to controlled disclosure (doc 282) without “panic publishing”?**
- **Can we reproduce the same digest from the same artifact inputs?**

## The drill: 30–60 minutes, single surface

Pick one surface each time (AuLD, ICLD, HoldCapsule, Disclosure Packet, SDS+TSR). Use a synthetic or non-sensitive dataset whenever possible.

### Inputs (minimum)
- A **surface**: `audit_log_digest` or `incident_command_log_digest` (or a small HoldCapsule summary).
- A **signing identity**: the key role used for SDS (`docs/285`) and its current key reference (`docs/286`).
- A **clock attestation**: optional RFC 3161 TSR (`docs/287`) or transparency log anchoring (`docs/284`).

### Outputs (minimum)
- A completed **Integrity Drill Report** using `artifacts/templates/hfv.integrity_drill_report.v1.json`.
- A stored, sealed digest artifact (HFV) plus signature material as appropriate (SDS).
- A short “what broke / what we fixed” note in the internal ops log (not a public artifact).

## Success criteria

A drill passes if all are true:
1. **Time-to-digest:** surface digest produced within the target SLA (e.g., ≤ 15 minutes).
2. **Reproducibility:** same inputs → same digest (document any nondeterminism).
3. **Key hygiene:** signatures validate and key refs match the current registry/rotation policy (`docs/286`).
4. **Disclosure discipline:** no raw logs released; any escalation uses a Disclosure Packet (`docs/282`).
5. **Receiptability:** optional but preferred—TSR or log-anchoring present and verifiable (`docs/287` / `docs/284`).

## Common failure modes (and the bounded fixes)

- **Non-deterministic digests** (ordering/normalization differences)  
  Fix: canonicalize sorting, time zone handling, and redaction transforms; record canonicalization rules.

- **Signature confusion** (wrong key, unknown policy, expired cert)  
  Fix: enforce key role separation; require key_ref + policy identifier in SDS; rotate keys intentionally.

- **Scope creep** (“just attach the raw log to be safe”)  
  Fix: require a Disclosure Packet for any raw release; record the allowed audience and redaction class.

- **Clock disputes** (when did this digest exist?)  
  Fix: prefer TSR or log anchoring for high-stakes surfaces; cross-check with witness co-sign if available.

## Cadence (suggested)

- **Weekly** during active election periods; **monthly** otherwise.
- Run at least one drill that exercises **controlled disclosure** end-to-end (doc 282), using synthetic data.

## External anchors (non-exhaustive)

- NIST incident response guidance emphasizes preparation and exercising response capabilities (SP 800-61r3).  
- CISA provides tabletop exercise resources that can be adapted to election ops contexts (CTEPs).

(See `docs/214-external-sources-index.md` for pinned references.)
