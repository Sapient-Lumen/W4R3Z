# Unreachability Proof Checklist

## Proof construction
- [ ] Target clearly identified (URL/host/IP/onion/content hash).
- [ ] Time window defined (start/end) and includes secure time proofs where possible.
- [ ] At least **n** independent vantages (distinct ASNs/regions/operators).
- [ ] At least one control target probed at the same time.
- [ ] Each probe result includes DNS/TCP/TLS/HTTP layer detail.
- [ ] Raw transcripts (or hashes) included for offline verification.

## Provenance
- [ ] Internal probes: signed by probe operator key.
- [ ] External measurements: immutable IDs recorded; raw results hashed.
- [ ] Independence claims documented (ASN/region/operator).

## Validation
- [ ] Confirm failures are not purely local (controls succeed on most vantages).
- [ ] Confirm failure mode indicates unreachability (timeouts/resets/NXDOMAIN, etc.).
- [ ] Confirm consistent failure for the protected endpoint class (evidence bundle, ATL, etc.).

## Publication
- [ ] Anchor URP into ATL within MAAD.
- [ ] Include URP hash in AWG gossip messages.
- [ ] If URP triggers policy threshold, execute pre-committed failover.
