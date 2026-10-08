# Security, Abuse, Threat Model, and Secret-Key-Material Review Runbook v1

1. Read `SECURITY_THREAT_MODEL.yml` and confirm every threat-model row has linked trust boundaries, abuse cases, and evidence artifacts.
2. Read `ABUSE_MISUSE_CASE_REGISTER.yml` and confirm every misuse case blocks an overclaim pattern rather than asserting mitigation completion.
3. Read `VULNERABILITY_DISCLOSURE_INTAKE.yml` and confirm it remains local issue routing, not a public VDP, bug bounty, CVE/CNA, CERT, or PSIRT service.
4. Read `SECURITY_HARDENING_BASELINE.yml` and confirm local tooling checks are not described as SAST, DAST, dependency scanning, or runtime hardening.
5. Read `TRUST_BOUNDARY_LEDGER.yml` and confirm authority, intake, tooling, and external-public boundaries are explicit.
6. Read `SECRET_KEY_MATERIAL_POLICY.yml` and confirm no secret/key-management claim is made and no public security contact is implied.
7. Run `python3 tools/check_security_abuse.py .` and write the six reports to `REGISTERS/`.
8. Rerun query regression, fixture corpus, release gates, reference integrity, and the archive validator.

This runbook does not create security compliance, penetration testing, public vulnerability handling, or cryptographic signing authority.
