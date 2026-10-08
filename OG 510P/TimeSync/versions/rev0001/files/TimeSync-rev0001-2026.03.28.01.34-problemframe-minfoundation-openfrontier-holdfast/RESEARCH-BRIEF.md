# RESEARCH BRIEF

This brief distills the external material that most influenced rev0001.

## NTP and NTS

RFC 5905 describes NTPv4 as widely used to synchronize computer clocks on the Internet.
RFC 8915 defines Network Time Security (NTS) as a cryptographic security mechanism for network time synchronization in the client-server mode of NTP.

Important implication:
NTS improves identity, authentication, replay resistance, and request-response consistency.
But RFC 8915 also says packet-delay attacks remain feasible in principle because NTP's offset estimation assumes roughly symmetric latency.

## Public timing services

NIST operates an Internet Time Service and also an authenticated NTP service.
That suggests a live distinction between:
- broad public dissemination,
- authenticated/trusted dissemination,
- and service-model expectations.

## PTP and precision timing

The Linux PTP Project describes PTP as an implementation of IEEE 1588 for Linux, aimed at robust precision synchronization.
This suggests that higher-precision and more controlled-environment synchronization already occupy a distinct design space from ordinary public NTP.

## PNT / GNSS risk posture

GPS.gov and NIST's Foundational PNT Profile both emphasize resilience, disturbance/manipulation detection, risk management, response, and recovery.
The PNT Profile is especially useful because it is not pretending timing is just a packet-format problem.

## Time semantics and UTC continuity

The 27th CGPM's Resolution 4 (2022) says the maximum value for UT1-UTC will be increased in, or before, 2035 and links this to continuity of UTC and the need for planning.
That is a signal that any ambitious time system should treat semantic assumptions about official global time explicitly.

## Uncertainty-bearing APIs

Spanner's TrueTime API exposes time as an interval `[earliest, latest]`.
This is a design signal, not a blueprint:
some applications benefit when uncertainty is exported rather than hidden.

## Secure rough-time bootstrap

In March 2026, the IESG approved the Roughtime document as an Experimental RFC.
This suggests continuing movement in the standards ecosystem toward secure, rough, inconsistency-reporting time mechanisms rather than one monolithic answer.

## Research takeaway

The ecosystem points away from a single naive replacement protocol and toward a layered problem:
- sources,
- trust,
- uncertainty,
- precision class,
- semantics,
- risk management,
- and downstream policy.
