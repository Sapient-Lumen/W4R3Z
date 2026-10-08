# Coercion-resistant registration & credentialing checklist

## Credential issuance
- [ ] Long-term credentials are hardware-backed and phishing-resistant (e.g., WebAuthn).
- [ ] Long-term credential NEVER signs ballots; it only authorizes issuance of unlinkable tokens.
- [ ] Recovery is in-person (or equivalently strong) with revocation transparency.

## Token issuance
- [ ] Eligibility tokens are unlinkable and spend-once.
- [ ] Issuance events are transparency-logged (hashes) to detect selective denial.
- [ ] Consider multi-issuer token issuance to reduce capture risk.

## Coercion mitigations
- [ ] If offering fake-credential mechanisms, document assumptions and usability risks.
- [ ] Provide supervised override where legally feasible.
