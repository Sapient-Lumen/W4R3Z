# PROBLEM LANDSCAPE

This note records the strongest things that seem justified after initial online research.

## 1) The landscape is already plural, not singular

The timing ecosystem is not one protocol and not one threat model.

- NTPv4 remains a major Internet synchronization mechanism.
- NTS adds cryptographic security to client-server NTP.
- PTP exists for higher precision synchronization, especially in more controlled environments.
- GNSS/PNT remains deeply important in infrastructure timing and also a major source of fragility.
- Roughtime is emerging as a useful secure rough-time mechanism.
- Application-level systems such as TrueTime show the value of exporting bounded uncertainty rather than a bare scalar timestamp.

This makes it unlikely that TimeSync should begin as "one protocol to replace everything."

## 2) Security does not erase timing uncertainty

NTS protects identity, authentication, replay resistance, and request-response integrity for NTP traffic.
That is important.

But delay attacks remain structurally hard:
if an adversary can asymmetrically delay packets in the path, cryptography does not solve the core estimation problem by itself.
This means TimeSync probably has to separate:

- **source authenticity**
from
- **time-estimate trustworthiness**

Those are related but not identical.

## 3) Timing is an operations and risk-management problem, not just a protocol problem

NIST's PNT profile emphasizes:
- identifying dependencies,
- identifying data sources,
- detecting disruption or manipulation,
- managing risk,
- responding,
- and recovering.

That is a strong clue about system shape.
TimeSync may need to be at least partly a risk/governance layer or profile, not merely a synchronization algorithm.

## 4) UTC itself has live institutional edges

The 27th CGPM decided in 2022 that the maximum value for UT1-UTC will be increased in, or before, 2035, with planning and coordination leading into that change.
This matters because it means the semantic ground under "official civil/atomic global time" is not entirely frozen.

TimeSync therefore should probably not silently bake in time semantics as if they were timeless and politically neutral.

## 5) Consumers need more than a timestamp

Spanner's TrueTime is valuable here as a conceptual signal:
it exports time as an interval with bounded uncertainty.

That does not mean TimeSync should copy TrueTime directly.
It does suggest that the narrow waist may need to expose:
- estimate,
- uncertainty,
- provenance,
- and possibly regime/confidence.

## 6) Public infrastructure already mixes trust, provenance, and service realities

NIST provides public Internet Time Service infrastructure and also an authenticated NTP service.
This is another clue that real deployments distinguish:
- public utility,
- trust model,
- and service guarantees.

## Tentative synthesis

The strongest current hypothesis is:

**TimeSync should begin as a specification and control surface for trustworthy time state across diverse timing mechanisms, rather than as a single replacement protocol.**

That hypothesis is still open.
