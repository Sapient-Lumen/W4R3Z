# Public evidence and disinformation resilience

**Track:** A (Deployable core)


Elections fail politically when the public cannot distinguish:
- true errors vs. false claims,
- isolated incidents vs. outcome-altering failures.

End-to-end verification helps, but only if the evidence is:
- accessible,
- independently reproducible,
- communicated without overclaiming.

## Threats
- Fake screenshots / fake receipts circulated at scale.
- Deepfakes / synthetic “official statements” and forged media designed to outrun verification.
- Claims that the log "forked" without evidence.
- Deliberate confusion about what is being verified (paper vs crypto vs vendor reports).

## Spec requirements

### Evidence package (MUST)

Treat public communications as evidence artifacts (see `186-incident-communications-as-evidence.md`). Publish signed notices (`hfv.public.notice`) that point to the relevant packet digests rather than relying on screenshots.
Publish a signed, content-addressed evidence package containing:
- election parameters (PK, contest definitions, hashes),
- witness checkpoints,
- ballot commitments/ciphertexts,
- proofs (shuffle/MPC/homomorphic),
- verifier outputs (multiple implementations),
- audit plan + final audit report.

### Reproducibility (MUST)
- At least two independent verifier implementations must reproduce the same results.
- Provide public test vectors and a "one-command" verification guide.

### Claim hygiene (MUST)
- Public communications must separate:
  - integrity evidence,
  - privacy assumptions,
  - coercion/malware residual risks.

## Operational practices
- Pre-election publish "what to check" guides for media/candidates.
- Run public tabletop exercises about likely misinformation scenarios.
- Publish a "known issues" registry and patch policy (template: `artifacts/registries/known-issues.csv`).
- Harden official comms channels (domain, TLS, email authentication) and monitor them as verification-critical surfaces; see `artifacts/checklists/official-communications-channels-hardening-checklist.md`.

## Reference points (informative)
- Risk framing for AI-era communications: `source: nist_ai_rmf_100_1_pdf`
- Common disinformation tactics (comms surface): `source: cisa_tactics_of_disinformation_508_pdf`
- Public-facing rumor-control patterns and myths-to-facts framing: `source: cisa_rumorcontrol_page`
- Baseline anti-spoofing for official email (SPF/DKIM/DMARC): `source: rfc7208_txt`, `source: rfc6376_txt`, `source: rfc7489_txt`
- SMTP downgrade/misconfig visibility (MTA-STS + SMTP TLS reporting): `source: rfc8461_txt`, `source: rfc8460_txt`
- Monitor certificate issuance for official domains (Certificate Transparency): `source: rfc9162_txt`
- Constrain certificate issuance for official domains (DNS CAA): `source: rfc8659_txt`
- Optional: enable DNSSEC for official domains (zone signing + DS at registrar): `source: rfc4033_txt`
- Baseline email + web security controls (operational hardening reference): `source: cisa_bod_18_01_page`
- Optional media provenance signal (Content Credentials / C2PA): `source: c2pa_content_credentials_spec_2_2_pdf`
