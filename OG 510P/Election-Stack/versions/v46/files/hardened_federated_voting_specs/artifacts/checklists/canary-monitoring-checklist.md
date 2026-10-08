# Canary monitoring checklist (targeted ballot manipulation)

## Coverage
- [ ] At least 3 independent operators run monitors.
- [ ] Monitors cover multiple regions and ISPs/ASNs.
- [ ] Monitors use diverse DNS resolvers and client stacks.

## What to record
- [ ] EPB hash + inclusion+consistency proofs.
- [ ] BD hash and content-length.
- [ ] Witness checkpoint IDs.
- [ ] TLS certificate chain metadata (for forensics).
- [ ] Timestamp and network path notes.

## Detection rules
- [ ] Any mismatch in EPB hash across monitors triggers an incident.
- [ ] Any mismatch in BD hash with the same EPB triggers an incident.
- [ ] Failure to obtain inclusion proof within deadline triggers a suppression incident.

## Evidence bundle
- [ ] Evidence bundle is signed.
- [ ] Bundle includes request/response hashes and proofs.
- [ ] Bundle is published and cross-anchored (multi-log notarization).

## Response
- [ ] Public status page updated with precise affected scope.
- [ ] Paper-of-record fallback activated for affected voters.
- [ ] EPB invalidated and re-ceremonied if compromise suspected.
