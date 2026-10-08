# 62 — Common Data Formats (CDFs) and interoperability

**Track:** A (Deployable core)


This pack assumes the voting ecosystem includes many independently operated systems:
registration, ballot definition, vote capture, tabulation, auditing, reporting, and archiving.

To reduce proprietary ambiguity and improve auditability, this document recommends aligning data interchange to the NIST Voting **Common Data Formats** (CDFs).

## Relevant NIST CDFs
- **Ballot Definition (BD)** — NIST SP 1500‑20.
- **Cast Vote Records (CVR)** — used for audits and comparisons.
- **Voter Records Interchange (VRI)** — voter registration/eligibility interchange.
- **Election Results Reporting (ERR)** — NIST SP 1500‑100r2.
- **Election Event Logging (EEL)** — NIST SP 1500‑101.

NIST also publishes implementation guidance that discusses practical cross-referencing and processing across multiple CDFs.

## Where CDFs fit in this architecture
### BD → EPB binding
- The BD file is hashed (JCS canonicalization) and bound into the ElectionParameterBundle.

### CVR + audit bridge
- If your tabulation system produces CVRs, they MUST be hash-chained and linked to:
  - BD hash
  - scanner/device identifiers
  - event logs (EEL)

This supports ballot-level comparison audits where allowed.

### ERR (results reporting)
- Publish results using a structured format (ERR) while enforcing a **DisclosurePolicy** (see tally-hiding doc) to mitigate pattern/coercion attacks.

### EEL (event logging)
- Publish sanitized event logs and hash commitments to full logs.
- Use EEL to support incident response and forensic review.

## Privacy cautions
NIST ERR supports reporting at very fine-grained levels (precinct/split precinct, ballot type, device). That can be useful operationally but can also increase privacy risk and enable pattern attacks.

**MUST:** the DisclosurePolicy pre-commits which breakdowns are allowed and enforces minimum cell sizes.

## Artifacts
- `artifacts/checklists/cdf-interoperability-checklist.md`

## References
- NIST SP 1500‑20 (BD).
- NIST GCR 24‑058 (implementation guidance).
- NIST SP 1500‑100r2 (ERR).
- NIST SP 1500‑101 (EEL).