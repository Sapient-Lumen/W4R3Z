# Routing & availability checklist (BGP/DNS/TLS)

**Track:** Shared (cross-cutting)


## BGP / routing
- [ ] RPKI ROAs published for all announced prefixes.
- [ ] ROV enabled on inbound routes for internal networks; policy for invalids defined.
- [ ] Route monitoring alarms configured (origin changes, unexpected AS paths, invalid announcements).
- [ ] Multi-homed across providers/regions; tested failover.

## DNS / domain
- [ ] Registrar lock enabled; MFA; change approvals; out-of-band verification.
- [ ] DNSSEC deployed where feasible; key rotation plan.
- [ ] Secondary domain(s) under independent registrar/control for emergency failover.

## TLS / certificates
- [ ] Certificate Transparency monitoring for mis-issuance alerts.
- [ ] Short-lived certs with automated rotation and strict change control.
- [ ] Emergency key compromise playbook (rotate, revoke, public notice, verifier updates).

## DDoS / overload
- [ ] Load tests include degraded mode (intake receipts still work).
- [ ] Multiple ingress endpoints + multi-path submission in clients.
- [ ] Public status page + mirrored evidence channels.

