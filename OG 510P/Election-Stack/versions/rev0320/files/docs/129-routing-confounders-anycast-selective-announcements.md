# 129 Routing Confounders: Anycast, Selective Announcements, and Interpretation Risk

**Track:** A+C (Core + North Star)


Routing policy can defeat naïve assumptions about “diversity” and “representativeness.”

## 129.1 Anycast selective announcements

Anycast networks frequently use selective announcements to steer inbound traffic.
This can create the illusion of global reachability while some regions are effectively served different endpoints or not served at all.

### Implications for evidence

- URPs must not assume that “same IP” implies “same service.”
- Endpoint validation MUST include the ElectionParameterBundle (EPB) hash and checkpoint IDs at the application layer.
- Probe cohorts MUST be diverse in ASNs and geography, and should include multiple targets (HTTP, DNS, OHTTP relay, etc.)

## 129.2 Modeling and inference limits

BGP hides policy details; monitoring may not reveal selective policy or diversion.
Thus:
- routing “health” cannot be inferred from control-plane feeds alone
- evidence must combine control-plane hints with data-plane measurements

## 129.3 Requirements

- Evidence endpoints MUST return signed HTTP Message Signatures bound to the content hash and checkpoint ID.
- Monitoring MUST compare *application-layer* artifacts (hashes) across vantages, not just reachability.
