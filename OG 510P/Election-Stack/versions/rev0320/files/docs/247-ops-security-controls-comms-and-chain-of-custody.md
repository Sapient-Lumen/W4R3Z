# 247 — Ops security controls: communications & chain of custody

**Track:** Shared

This note treats **public communications** and **chain of custody** as *first-class security controls*:
they reduce the attack surface for misinformation, provide verifiable operational discipline, and
create audit-ready artifacts **without** bloating the evidence corpus.

This document is intentionally small. It points to canonical guidance and provides **archive-native**
ways to express the minimum useful outputs.

---

## 247.1 Two controls that quietly do a lot of work

### A. Public communications (as an infrastructure control)

When the public cannot quickly find consistent official information, attackers can:
- amplify confusion (lower trust → higher operational load),
- create “split-view” narratives (different audiences see different alleged facts),
- force officials into reactive comms during incidents.

EAC/CISA provide a planning-oriented guide with worksheets for **message / audience / timing / partners / team / prepare / review**. Use it as the external “how to run comms” anchor.  
**Anchor:** *Enhancing Election Security Through Public Communications* (May 2024).  
Source: https://www.eac.gov/sites/default/files/2024-06/Enhancing_Election_Security_Through_Public_Communications.pdf

For incident moments (cyber/physical/disinformation), EAC/CISA also publish an incident-response communications guide with templates and considerations.  
**Anchor:** *Election Infrastructure Incident Response Communications Guide* (Oct 2024).  
Source: https://www.eac.gov/sites/default/files/2024-10/Election_Infrastructure_Incident_Response_Comms_Guide_508.pdf

Archive-native representation:
- Use **`PublicNotice`** (`186`) for official statements as evidence objects.
- Use **`OfficialChannelDirectory`** (`203`) + **parity** (`104`) so multiple channels converge on the same notice digests.
- Use “myth → fact → how to verify” patterns for rumor control (`186`, `195`).

### B. Chain of custody (as a tamper-evidence control)

Chain of custody practices constrain post-hoc disputes by making “who had what, when” auditable.
EAC provide a best-practices report explicitly oriented to election materials and systems.  
**Anchor:** *Chain of Custody Best Practices* (EAC).  
Source: https://www.eac.gov/sites/default/files/bestpractices/Chain_of_Custody_Best_Practices.pdf

Archive-native representation (minimal):
- Treat **every physical transfer** as producing a tiny, signed “handoff record” envelope (see `173`, `176`) that references:
  - container/seal IDs (structured fields),
  - timestamps + custodians,
  - photo hashes (optional, referenced as detached payloads),
  - a link to the relevant `PublicNotice` digest (if the transfer is part of an announced process).

If your jurisdiction already has paper forms, do **not** copy them into the archive; instead:
- define a small schema that captures the **shared invariants**, and
- record a mapping: “form field → schema field” (one page).

---

## 247.2 A tiny control matrix (what this archive expects you to be able to prove)

| Control | “Proof” you can publish safely | Archive surface |
|---|---|---|
| Official channels are recognizable | OfficialChannelDirectory + DNS/TLS/email posture snapshot | `203`, `199` |
| Messages are consistent | Same `PublicNotice` digests across channels (parity snapshots) | `186`, `195`, `104` |
| Incident comms are rehearsed | Dated drill notice + after-action note (hashes only) | `186` (+ internal SOP elsewhere) |
| Custody is continuous | Handoff envelopes + seal reconciliation logs (hashes, not scans) | `173`, `176` |
| Disputes are bounded | Public pointers to audit steps + what evidence exists | `195`, `09`, `246` |

---

## 247.3 “Don’t bloat” rules for ops artifacts

1. Prefer **hashes + reproducible procedures** over storing scans/screenshots.
2. Publish only what is safe: never leak PII or operational secrets.
3. If a document is jurisdiction-specific policy, store **a pointer and a one-paragraph delta**, not the full SOP.
4. If you can’t imagine an outsider verifying it, it probably shouldn’t be “evidence”.

---

## 247.4 Related anchors

- CISA: Best Practices for Securing Election Systems: https://www.cisa.gov/best-practices-securing-election-systems
- NIST: Cybersecurity Framework Election Infrastructure Profile (2024): https://www.nist.gov/publications/cybersecurity-framework-election-infrastructure-profile
- CEIR: 2024 Voter Registration Database Security Report (published Sep 18, 2025): https://electioninnovation.org/research/2024-vrdb-security-report/

