# Emergency patch mode (“grafts”, but auditable)

Problem: urgent security fixes sometimes need speed that conflicts with “rebuild everything”.

Guix uses “grafts” to deliver critical updates quickly. The DeriveBSD stance is to support an equivalent *only if* it is:
- explicit
- policy-governed
- time-bounded
- explainable

## DeriveBSD design constraints

- A graft produces a **new Plan** and **new closure proof** (no silent mutation).
- The graft is represented by an **override record** that:
  - names what is overridden
  - cites the vulnerability/incident context
  - carries an expiry and revocation path
  - is included in evidence digests for `derive explain`

## Operational posture

- default policy: grafts disallowed
- high-assurance policy: allow only for specific package classes, with additional signatures

See RFC-0071.

Related: signed revertible patchsets (syspatch-style) are a complementary *distribution* mechanism for small deltas; see `docs/113-syspatch-style-patchsets.md` (RFC-0081).
Last updated: 2026-02-23
