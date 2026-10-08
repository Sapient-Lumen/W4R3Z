# Routing, DNS, and availability attacks (anti-censorship engineering)

**Track:** A (Deployable core)


Voting systems fail more often from **availability and routing problems** than from clever cryptanalysis.
This doc makes network-layer paranoia explicit.

## Threats

- **DDoS** (volumetric, application-layer, targeted at ingress, witnesses, or verifiers).
- **BGP hijacking / interception** (traffic diverted, selectively dropped, or MITM'd).
- **DNS attacks** (cache poisoning, registrar compromise, domain seizure).
- **Certificate mis-issuance** (CA compromise, wrong certs used for MITM).
- **CDN or cloud control plane compromise** (config pushes, edge compute abuse).
- **Network partitions** (regional outages, geopolitical blocks, submarine cable cuts).

## Design posture

1. The bulletin board is **replicated** and has multiple independently operated ingress points.
2. “Recorded” is only true when the voter has a **Merkle inclusion proof** against a
   **witness-quorum checkpoint** (not merely “server said ok”).
3. Provide **multi-path submission**: clients may submit to N ingress domains / IPs and accept
   the first receipt that reaches quorum.

## Concrete mitigations (defensive playbook)

### Routing security
- Publish **RPKI ROAs** for your prefixes and deploy **Route Origin Validation** internally.
- Continuously monitor route announcements (invalids, sudden path changes), and publish alerts.
- Prefer multi-homing across providers and regions.

### DNS and domain control
- Use registrar lock, MFA, and out-of-band change control.
- Deploy **DNSSEC** for authoritative zones where feasible.
- Consider multiple independently controlled domains (failover that does not share registrar).

### TLS/cert defenses
- Use Certificate Transparency monitoring and rapid incident playbooks for mis-issuance.
- Consider short-lived certs and automated rotation with strong change control.
- For official comms surfaces (status pages, press pages), baseline web/email hardening guidance is a useful starting point (`xref: cisa_bod_18_01_page`).

### DDoS resilience (don’t just “buy a CDN”)
- Anycast + rate-limits are table stakes, not a plan.
- Run “degraded mode” that still returns **intake receipts** and quickly posts ballots when stable.
- Publish a public status page and alternate submission paths (mirrors, Tor onion, etc.) *if policy allows*.

## Evidence of censorship / dropping

Require a two-phase flow:
1. **IntakeReceipt**: server acknowledges receipt with a deadline for inclusion.
2. If not included by deadline, the voter can publish a signed “non-inclusion claim” with the intake proof.

This turns silent suppression into **public, auditable evidence**.

## Primary references
See `references.md` for RPKI best practices and “stealthy hijacking” analysis under incomplete ROV adoption.
