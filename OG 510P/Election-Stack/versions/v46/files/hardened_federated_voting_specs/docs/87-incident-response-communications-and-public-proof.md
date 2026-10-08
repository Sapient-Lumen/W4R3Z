# 87 — Incident Response Communications & Public Proof

**Track:** A (Deployable core)


## Principle
Attackers often win by **confusion**, not by cryptography.

Communications MUST:
- be fast,
- be precise about what is known vs unknown,
- avoid over-claiming,
- be anchored in verifiable artifacts (hashes, checkpoints, inclusion proofs).

## Canonical public facts (publishable)
When safe and lawful, publish:
- latest witness-quorum checkpoint (ID, hash)
- ElectionParameterBundle (EPB) hash and inclusion proof
- evidence bundle manifest hashes
- drift alerts (ENR vs canonical results) + anchoring proof

## Statement tiers
1) **Status** (routine): system operating; checkpoint cadence OK.
2) **Degraded**: partial outage, witness quorum reduced, higher latency.
3) **Incident**: integrity or availability risk; investigations ongoing; mitigation in progress.
4) **Emergency freeze**: stop accepting ballots, preserve evidence, invoke recovery path.

## Mandatory “truthfulness rules”
- Never claim “votes are safe” without stating the basis (e.g., “No integrity alerts; all receipts verified against checkpoint X”).
- Never claim finality; always distinguish **unofficial** vs **certified**.
- Never reference internal logs as proof without publishing hashes or third-party attestations.

## Coordination
Communications must coordinate with:
- election officials
- witness/trustee operators
- VRDB operators
- incident response partners

## Artifacts
- Template: `artifacts/templates/incident-communications.md`
- Template: `artifacts/templates/public-statement-template.md`
- Schema: `schemas/IncidentCommsPackage.json`

## “Proof-first” comms checklist (abridged)
- [ ] Identify checkpoint IDs and hashes relevant to the claim.
- [ ] Publish statement with explicit uncertainty.
- [ ] Publish/update status page with signed statement.
- [ ] Preserve evidence bundle and record chain-of-custody.
- [ ] Pre-brief independent observers/verifiers on how to validate.