# Requirements traceability matrix (starter)

**Track:** A (Deployable core)


This doc maps our requirements to:
- public election guidance (risk management),
- certification directions (VVSG + EAC E2E process),
- software/supply-chain frameworks (SSDF, C-SCRM).

It prevents “security theater” by forcing each claim to point to evidence.

## Mapping table (minimum)
| Requirement | Where specified here | Evidence target |
|---|---|---|
| Detect equivocation / split-view | 04, 23 + schemas | ForkProof produced by independent witnesses |
| Verifiable “recorded-as-cast” | 14 + 04 | inclusion proof validates vs checkpoint |
| No single party can decrypt ballots | 05 | threshold ceremony transcript + public proofs |
| Remote return risk disclosed | 01, 12 | public threat model + explicit non-claims |
| Supply-chain hardened | 17 | provenance + SBOM + reproducible build attestations |
| Incident response + recovery | 08, 09, 18 | game-day drills + postmortems |
| Public incident notices as evidence | 186, 87 + schemas | signed PublicNotice envelopes + receipted publication |
| Disinformation resilience (forged media / receipts) | 37, 27 | public rumor-control packet + verifier reproduction |

## Next steps
- Add REQ-IDs and tie each REQ to a test plan and artifacts.
- Map to jurisdiction-specific certification / legal constraints.