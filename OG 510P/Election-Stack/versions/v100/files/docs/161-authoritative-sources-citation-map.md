# 161. Citation map (lockfile IDs → sources)

**Track:** Shared


This archive uses `evidence/lock/external-sources.toml` to pin authoritative external sources.
Normative docs SHOULD reference **lockfile IDs** rather than embedding fragile URLs.

## 161.1 How to cite a source in this archive

Preferred form in docs:

- `source: <lockfile id>`

Example:

- `source: rfc9162_txt`

## 161.2 Current pinned sources (v46+)

See `evidence/lock/external-sources.toml`. The pinned set includes (examples):
- CT v2 (RFC 9162)
- DNS CAA (RFC 8659) (constrain certificate issuance for official domains)
- DNSSEC introduction/requirements (RFC 4033) (optional hardening for official domain integrity)
- RATS architecture (RFC 9334)
- EAT (RFC 9711)
- JSON Canonicalization Scheme (RFC 8785)
- HTTP Message Signatures (RFC 9421)
- SPF (RFC 7208) + DKIM (RFC 6376) + DMARC (RFC 7489) (baseline anti-spoofing for official election email domains)
- MTA-STS (RFC 8461) + SMTP TLS Reporting (RFC 8460) (visibility into downgrade/misconfig for email delivery)
- SCITT architecture draft (-22)
- SCITT receipts profile draft (-00)
- SCITT reference APIs draft (SCRAPI -07)
- VVSG 2.0 Test Assertions v1.4
- National Academies “Securing the Vote” highlights
- NIST SP 800-204D (CI/CD supply-chain security)
- NIST Cybersecurity Framework (CSF) 2.0 (CSWP 29)
- NIST SP 800-61r3 (incident response recommendations; CSF 2.0 community profile)
- in-toto Attestation Statement v1 + SLSA provenance predicate
- EAC incident response communications guide (PDF hash pinned; PDF not bundled)
- EAC/CISA public communications guide (PDF hash pinned; PDF not bundled)
- EAC AI Toolkit for election officials (PDF hash pinned; PDF not bundled)
- EAC comms toolkit for pre/post election processes (HTML; informative until pinned)

- NIST AI RMF 1.0 (NIST AI 100-1)
- CISA 'Tactics of Disinformation' (informative comms reference)
- CISA Election Security 'Rumor vs. Reality' landing page (informative public rumor-control reference)
- CISA BOD 18-01 (baseline email + web security controls for official comms channels)
- CISA best practices for securing election systems (operational hardening reference)
- C2PA Content Credentials technical specification (informative media provenance)
Some sources may be listed but temporarily unpinned (sha256 empty) due to access restrictions or because they are mutable HTML pages. Treat unpinned sources as **informative** until pinned or replaced with an immutable artifact.

## 161.3 Precedence order (recap)

When sources conflict, prefer:
1. binding law/regulation (jurisdiction-specific)
2. election authority certification standards (e.g., EAC/VVSG)
3. NIST publications and formats
4. IETF RFC Editor publications
5. peer-reviewed research
6. vendor blogs/whitepapers (informative only)

## 161.4 Drift triggers

If a pinned source changes (sha mismatch) or a new upstream version is published:
- file an ADR,
- update affected claims/evidence lanes,
- and bump `VERSION` if interoperability semantics could change.
