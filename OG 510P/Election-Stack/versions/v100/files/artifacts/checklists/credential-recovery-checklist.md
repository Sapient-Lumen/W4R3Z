# Credential recovery checklist (election-week)

## Before election
- [ ] Publish recovery policy (hours, locations, required evidence, appeal path).
- [ ] Train staff on abuse-safe handling and privacy.
- [ ] Pre-position spare authenticators / issuance kits.
- [ ] Drill “lost device” and “coercion/abuse” flows.

## During election
- [ ] Offer **backup authenticator** path first (if enrolled).
- [ ] If voter selects “I’m not safe,” route to high-safety channel; avoid screens/printouts that confirm status.
- [ ] Revoke lost credential promptly; issue new credential ID.
- [ ] Mint new eligibility tokens; invalidate unused old tokens if policy allows.
- [ ] If digital recovery fails, provide paper-of-record fallback.

## After recovery
- [ ] Record `CredentialLifecycleEvent`.
- [ ] Publish aggregate metrics (no PII).
- [ ] Provide dispute filing instructions.
