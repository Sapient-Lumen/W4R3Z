# 161. Citation map (lockfile IDs → sources)

**Track:** Shared


This archive uses `evidence/lock/external-sources.toml` to pin authoritative external sources.
Normative docs SHOULD reference **lockfile IDs** rather than embedding fragile URLs.

## 161.1 How to cite a source in this archive

Preferred form in docs:

- `source: <lockfile id>`

Example:

- `source: rfc9162_txt`

## 161.2 Current pinned sources (v38)

See `evidence/lock/external-sources.toml`. The pinned set includes:
- CT v2 (RFC 9162)
- RATS architecture (RFC 9334)
- EAT (RFC 9711)
- JSON Canonicalization Scheme (RFC 8785)
- SCITT architecture draft (-22)
- SCITT receipts profile draft (-00)
- SCITT reference APIs draft (SCRAPI -07)
- NIST Interoperable Randomness Beacons overview
- drand distributed randomness beacon docs
- VVSG 2.0 Test Assertions v1.4
- National Academies “Securing the Vote” highlights
- NIST SP 800-204D (CI/CD supply-chain security)
- in-toto Attestation Statement v1 + SLSA provenance predicate

Some sources may be listed but temporarily unpinned (sha256 empty) due to access restrictions.

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
