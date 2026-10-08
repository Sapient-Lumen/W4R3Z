# Publicly tally-hiding & results disclosure policy (pattern-attack hardening)

**Track:** A (Deployable core)


Many election ecosystems publish fine-grained tallies (precinct-by-precinct, contest-by-contest).
This can enable **pattern / “Italian” attacks** and can degrade privacy for voters and candidates.

This document defines a **DisclosurePolicy** object that is committed pre-election (inside the
ElectionParameterBundle) and enforced at publication time.

## Threats

- Pattern coercion / vote buying via uniquely identifying tally patterns
- Small-cell privacy leakage (rare contests, tiny precincts)
- Targeted suppression enabled by near-real-time turnout/partial tallies

## Strategy menu

### A) Tally hiding (strongest against pattern attacks)
Publish only:
- winners, final totals, and legally required aggregates
- no per-ballot or overly granular aggregates

Research has proposed “publicly tally-hiding verifiable e-voting” to preserve verifiability while hiding
granular tally information. (See Kryvos references.)

### B) Coarsening + suppression (practical default)
- Define minimum cell size thresholds for breakdown publication
- Suppress or merge cells below threshold
- Delay publication of granular breakdowns until after certification (if ever)

### C) Differential privacy (only for election-adjacent datasets)
Differential privacy is *not* appropriate for official certified totals, but may be suitable for
optional auxiliary releases (e.g., research datasets, certain turnout analytics) when evaluated and
communicated correctly.

## Requirements (normative)

- The election MUST publish a signed `DisclosurePolicy` before voting opens.
- Verifiers SHOULD reject result packages that violate the committed policy.
- “Unofficial partial results” MUST include a policy statement about volatility and certification.

## References

- Kryvos: Publicly tally-hiding verifiable e-voting (Italian attack discussion)
- NIST: guidance on evaluating differential privacy claims (for auxiliary releases)