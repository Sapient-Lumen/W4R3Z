# ADR 0003: Treat institutional volatility as a first-class risk (without expanding Track A claims)

**Track:** Shared (cross-cutting)


- Status: **Accepted**
- Date: **2026-02-27**

## Context

Election integrity depends on more than “the crypto”: certification regimes, test labs, vendors, election offices, and
official communications channels are all part of the real-world system.
These institutions can be compromised, captured, defunded, or simply make mistakes — and adversaries exploit that
volatility to create legitimacy crises (even when ballots and tabulation are sound).

This archive already contains capture-resistance surfaces (witness governance, verifier diversity, registry capture response,
PublicNotice as evidence), but Track A’s *threat model* and *results publishing* lane did not name “institutional volatility”
as an explicit adversary class.

## Decision

1) Add a scoped Track A adversary class for **institutional / certification ecosystem compromise** (see `../docs/01-threat-model.md`).
2) Treat “what institutions claim” as **inputs that must be bound to evidence**, not as trusted premises:
   - cite pinned versions of load-bearing standards (`../docs/151` / `../docs/161`);
   - keep official comms channels discoverable and auditable (official-channels registry, `../docs/203–205`);
   - treat ENR/results publishing as a security boundary with replayable signed artifacts (`../docs/63` / `../docs/68`).
3) Keep Track A claims conservative: this ADR does **not** claim to solve institutional capture; it only requires
   that the *system’s dependence on institutions* be visible and that failures become provable.

## Consequences

- Threat modeling and assurance discussions can address governance/certification volatility explicitly without drifting into
  political claims.
- Maintainers must keep standards citations pinned and “source vs xref” hygiene tight.
- Operator guidance should prefer *auditable procedures* over “trust the authority” narrative.

## Follow-ups

- Ensure `../docs/19-certification-and-standards-alignment.md` and the ENR/results-pipeline lane carry compact, pinned references.
- Consider a small “institutional risk register” artifact only if it can be kept stable and size-disciplined.
