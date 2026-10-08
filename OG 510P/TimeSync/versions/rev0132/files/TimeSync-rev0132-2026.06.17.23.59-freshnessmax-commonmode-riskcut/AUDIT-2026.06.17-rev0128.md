# TimeSync rev0128 audit — authposture-ntpdata-nooverclaim

## Risk selected

The riskiest remaining seam after rev0127 was trust overclaim. The chrony adapter had become good at preserving operational evidence, but authentication information was absent. The dangerous failure mode was not merely missing security telemetry; it was the possibility that a later adapter would see `NTS` or `Authenticated: Yes` in chrony output and silently upgrade source posture or profile conformance without TimeSync verifying the cryptographic evidence itself.

## Changes made

- Added `chronyc authdata -a` and `chronyc -n ntpdata` roles to the capture envelope and fake-live harness.
- Added example chrony authentication reports.
- Parsed authentication rows and ntpdata blocks into `chrony_observation.authentication_summary`.
- Added an `authentication_posture` extension hook with `verified_by_timesync=false`, `used_for_decision=false`, and `profile_strengthening=none`.
- Added `CHRONY-P1-AUTH-REPORTED-NO-OVERCLAIM` using high-distance evidence plus reported authentication.
- Added independent-evaluator checks that reject any observation claiming TimeSync used reported authentication for decision strengthening.
- Extended the RFC 9249 crosswalk guard so authentication telemetry is adapter-local and forbidden for core promotion.

## Audit/refactor result

Authentication posture now has a single explicit boundary:

```text
chrony-reported authentication -> adapter-local diagnostics -> no TimeState strengthening
```

This avoids two wasteful futures: leaving authentication information invisible, or adding a premature trust registry that claims more than the implementation can prove. The output is useful to a human or later verifier, but it does not change the six-field decision result.

## Severe/wasteful issue corrected

Before rev0128, there was no executable guard against authentication theater. A future high-distance capture could have shown `NTS` and been treated as more trustworthy simply because the string appeared in a management command. rev0128 makes that impossible in the chrony vertical slice: reported authentication is visible, but unsafe timing evidence remains unsafe.

## Still open

- No NTS packet, cookie, TLS certificate, AEAD tag, or NTP extension-field verification is performed.
- No symmetric-key MAC verification is performed.
- The live path is still exercised through a fake `chronyc`, not a real chronyd/chronyc host in this cloud container.
- UTC is chrony-reported and unqualified; named UTC realization is not proven.
- Leap-smear policy discovery is not implemented.
- RFC 9249 remains a comparison guard, not proof of interoperability.
