# 117 — Automated Unreachability Proofs with RIPE Atlas (URP-Atlas)

**Track:** A (Deployable core)


This doc specifies an *automatable* pipeline to generate **UnreachabilityProof (URP)** objects using
**RIPE Atlas** measurements as independent, multi‑vantage corroboration.

> Goal: during an attack, generate **court-usable** evidence that an endpoint was selectively unreachable
> (e.g., by ASN/region/device) *without requiring manual ad‑hoc screenshots*.

## Threats addressed
- Selective unreachability / censorship with plausible deniability
- Split-world delivery of evidence (some audiences see “up”, others see “down”)
- “Works for me” disputes where only local telemetry exists

## High-level flow
1. **Plan**: Build an `AtlasMeasurementPlan` (targets + probe sets + cadence + ethics guardrails).
2. **Create measurement**: Use RIPE Atlas Measurements API (authenticated) to create HTTP/DNS/ICMP checks.
3. **Fetch results**: Use the measurement results endpoint over a bounded window (`start`/`stop`).
4. **Reduce**: Convert raw results into deterministic *reachability claims* + control comparisons.
5. **Build URP**: Produce `UnreachabilityProof.json` referencing:
   - measurement IDs
   - probe set criteria (country/ASN/tags)
   - time window
   - deterministic reduction outputs
   - raw-results hashes + storage pointers
6. **Sign + anchor**: Include in `OutageAttestation` / `AvailabilityTransparencyEntry`, then checkpoint.

## Design constraints (paranoid)
- Treat RIPE Atlas as **independent but not authoritative**. Always include:
  - *controls*: targets you expect to remain reachable (e.g., major public resolvers, your own “control” host)
  - *multi-method corroboration*: DNS + HTTPS + ICMP where feasible
- Maintain strict **ethics guardrails** (see `118-measurement-ethics-guardrails.md`):
  - minimize load; avoid “port scanning”; prefer HTTP(S) HEAD/GET with small payload; honor platform terms
- Avoid leaking voter traffic: URP-Atlas probes should never embed voter identifiers or per-voter tokens.

## Deterministic reduction rules (normative)
Given a measurement result set R for target T over window W:
- A probe observation is **Reachable** iff:
  - HTTP: status code in {200..399} with TLS handshake success (if https)
  - DNS: response received with valid format (rcode 0 or expected NXDOMAIN) and RTT < policy threshold
  - ICMP: echo reply received with RTT < policy threshold
- A probe observation is **Unreachable** iff:
  - transport failure / timeout / DNS failure / TLS failure / connect failure
- A probe is **Indeterminate** iff:
  - probe reports local failures not attributable to target (e.g., “probe busy”, known probe errors)
- A target T is **Unreachable in cohort C** iff:
  - At least `k` probes in C have Unreachable
  - and Unreachable rate in C exceeds `p%`
  - and controls remain Reachable in C (or else downgrade to “Network-wide impairment”)

All thresholds MUST be part of the signed `AtlasMeasurementPlan`.

## Data retention
- Store raw results (or a canonical subset) in content-addressed storage.
- Store a hash of raw results and the exact `start/stop` window in the URP.

## Artifacts
- Schema: `schemas/AtlasMeasurementPlan.json`
- Example: `artifacts/examples/atlas_measurement_plan_example.json`
- Tool: `tools/atlas_urp_generator.py` (research/prototype; dry-run emits a reviewed payload and `--create` fails closed unless operator review is explicit)
