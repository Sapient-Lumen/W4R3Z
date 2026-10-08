# 62 — Common Data Formats (CDFs) and interoperability

**Track:** A (Deployable core)


This pack assumes the voting ecosystem includes many independently operated systems:
registration, ballot definition, vote capture, tabulation, auditing, reporting, and archiving.

To reduce proprietary ambiguity and improve auditability, this document recommends aligning data interchange to the NIST Voting **Common Data Formats** (CDFs).

## Relevant NIST CDFs
- **Ballot Definition (BD)** — NIST SP 1500‑20. (`source: nist_sp1500_20_bd_pdf`)
- **Cast Vote Records (CVR)** — used for audits and comparisons. (`source: nist_sp1500_103_cvr_pdf`)
- **Voter Records Interchange (VRI)** — voter registration/eligibility interchange. (`source: nist_sp1500_102_vri_pdf`)
- **Election Results Reporting (ERR)** — NIST SP 1500‑100r2. (`source: nist_sp1500_100r2_err_pdf`)
- **Election Event Logging (EEL)** — NIST SP 1500‑101. (`source: nist_sp1500_101_eel_pdf`)

NIST also publishes implementation guidance that discusses practical cross-referencing and processing across multiple CDFs (`xref: nist_gcr_24_058_cdf_implementation_guidance_pdf`).

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
- NIST SP 1500‑20 (Ballot Definition CDF). `source: nist_sp1500_20_bd_pdf`
- NIST SP 1500‑103 (Cast Vote Records CDF). `source: nist_sp1500_103_cvr_pdf`
- NIST SP 1500‑102 (Voter Records Interchange CDF). `source: nist_sp1500_102_vri_pdf`
- NIST SP 1500‑100r2 (Election Results Reporting CDF). `source: nist_sp1500_100r2_err_pdf`
- NIST SP 1500‑101 (Election Event Logging CDF). `source: nist_sp1500_101_eel_pdf`
- NIST GCR 24‑058 (Implementation Guidance for Common Data Formats). `xref: nist_gcr_24_058_cdf_implementation_guidance_pdf`