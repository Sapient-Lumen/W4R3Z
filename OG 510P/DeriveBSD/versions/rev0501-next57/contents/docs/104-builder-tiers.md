# Builder strategy tiers (jails first, microVM optional)

DeriveBSD treats builders as hostile, but also needs speed.

## Tier 1: jail-backed builders (default)

- fast, cheap isolation
- deny network by default
- no secret material in build jails
- outputs must be verified by digest + signature + policy

## Tier 2: microVM-backed builders (optional)

- stronger isolation boundaries
- useful for high-assurance builds or untrusted toolchains
- same evidence chain as Tier 1 (Plan → outputs)

## Why two tiers

- “secure by default” without making development unusable
- policy can require Tier 2 for specific targets

Optional: standardize builder pools around Remote Execution API semantics (CAS + ActionCache) for distributed builds (`docs/136-remote-execution-api-builder-pools.md`).

See RFC-0073.
Last updated: 2026-02-23
