# 282 — Controlled disclosure + redaction pipeline for evidence surfaces

**Track:** Shared

This doc defines a *minimal* pipeline for disclosing **raw excerpts** (when required) from digest‑first evidence surfaces (`278–281`) without turning the archive into a public data leak.

The goal is to make “we can disclose” mean **repeatable, reviewable, and provable**, not “someone copy/pasted logs into a PDF.”

---

## Core rule

1) **Publish digests by default** (AuLD / ICLD / HoldCapsule).  
2) **Disclose raw excerpts only via a Disclosure Packet** (below), under a defined authority and review path.

> If a fact can be supported by digests + scope declarations, do not escalate to raw disclosure.

---

## Threat model: what disclosure breaks

Raw disclosures can unintentionally reveal:
- **PII** (voter identity, addresses, signatures, phone numbers),
- **sensitive operational details** (credentials, internal topology, threat intel),
- **protected communications** (attorney–client, deliberative process, protected sources),
- **attack surfaces** (exact log formats, suppression points, rate limits, monitoring gaps).

Therefore: *disclosure is a controlled operation*, not a document attachment.

---

## Minimum Disclosure Packet (MDP)

A Disclosure Packet is a bounded bundle that contains:

1. **Cover sheet** (authority, scope, purpose, requestor, legal basis if any)  
2. **Selection manifest** (what records/excerpts were selected, from where)  
3. **Redaction log** (each redaction: reason + method + reviewer)  
4. **Integrity anchors** (hashes of raw items, hashes of redacted items, linkage to digest surface IDs)  
5. **Custody notes** (who handled the packet, when, and under what policy)

Use template: `artifacts/templates/hfv.controlled_disclosure_packet.v1.json`.

---

## Redaction policy (minimum)

Redaction should be **structured** and **auditable**:

### Allowed redaction classes
- **PII** (including quasi‑identifiers that re‑identify when combined)
- **Secrets** (credentials, keys, tokens, session IDs, internal endpoints)
- **Protected communications** (privileged or legally protected material)
- **Safety** (credible threats, doxxing vectors, vulnerable persons)
- **Vendor / third‑party constraints** (only when tied to contractual necessity)

### Disallowed redaction reasons
- “Embarrassing”
- “Politically inconvenient”
- “May reduce confidence”
- “Hard to explain”

If an item is withheld for a disallowed reason, the packet must instead record a **non‑disclosure rationale** and escalate to governance.

---

## Operational steps (smallest viable)

1. **Request intake** → record requestor, question, deadline, and authority
2. **Locate** → map the request to one or more digest surfaces and their scope planes
3. **Select** → choose the *minimum* excerpts needed to answer the question
4. **Redact** → apply allowed redaction classes; record each action in the redaction log
5. **Seal** → compute hashes for raw + redacted; bind to relevant digest IDs (AuLD/ICLD/HoldCapsule)
6. **Release** → deliver through approved channel; record custody and release conditions
7. **Post‑release** → publish a public *notice of disclosure* where appropriate (without raw content)

---

## What to publish publicly (safe default)

If you need to “show your work” publicly:
- publish **digest updates** (new segment hashes, new scope declarations),
- publish a **disclosure notice** (what was disclosed, to whom, under what authority, and which digest IDs it maps to),
- publish **aggregates** (counts, rates, timelines) rather than raw lines.

---

## External anchors to pin

- NIST SP 800‑92 (Log Management) — operational guidance for logging programs
- NIST SP 800‑122 (PII Confidentiality) — baseline PII handling concepts

(See `evidence/lock/external-sources.toml` + `docs/214-external-sources-index.md`.)


## Optional: transparency-log anchoring

If you need public or multi-party auditability of *when* a digest existed, anchor the digest hash to an append-only transparency log and record the handle in the HFV `transparency_log` block (see `284`). Keep inclusion proofs in a Disclosure Packet (`282`) unless governance requires public release.
