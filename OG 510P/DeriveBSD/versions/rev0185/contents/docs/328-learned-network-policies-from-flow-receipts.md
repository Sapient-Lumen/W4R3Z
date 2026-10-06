# Learned network policies from flow receipts (audit mode → reviewable diffs)

DeriveBSD already treats outbound networking as **brokered authority**:
- services request leases via the egress broker
- the broker emits `net.flow.receipt` evidence
- policy binds “what this unit may talk to” to named classes (`net.egress.policy`)

The adoption trap is the same as filesystem/Capsicum profiles: **hand-authoring good network policy is hard**.
Greenfield advantage: bake in a learn→review→enforce loop that makes *least-network* cheap.

## Prior art: observe-first network policy generation

Several ecosystems learned that “deny-by-default networking” only works if you can *first* observe and summarize real traffic:

- **Cilium policy audit mode**: allow traffic while logging what network policy *would have denied*, so you can iteratively converge on rules. (This is explicitly *not* production-recommended as a steady state.)
  - https://docs.cilium.io/en/latest/security/policy-creation.html

- **Kubescape network policy generation**: capture aggregated traffic into a “network neighborhood” object, then generate Kubernetes `NetworkPolicy` on demand.
  - https://kubescape.io/docs/operator/network-policy-generation/

- **Calico log rules**: add high-priority logging policies to see traffic patterns that are not currently handled by your policies.
  - https://docs.tigera.io/calico/latest/network-policy/policy-rules/log-rules

Common shape:
1) collect observed flows
2) aggregate/summarize (reduce noise)
3) generate candidate rules
4) require review before enforcement

## DeriveBSD proposal: `derive learn net` (flows → policy patches)

Introduce a first-class learning workflow for network authority that mirrors `docs/326-learned-promise-profiles-and-observation-mode.md`.

### `derive learn net <unit> --suite <tests>`

Runs the unit (or its test suite) with:
- normal egress-broker mediation enabled
- an **audit mode** switch that records “would have been denied” outcomes if an intended target class is missing
- an explicit bounded session window (time + max events)

Produces:
- a bounded evidence bundle:
  - `net.flow.receipt` objects
  - optional `net.dns.query.receipt` objects (if DNS mediation is enabled)
- an aggregated summary object (human-readable + machine-derivable):
  - `net.flow.summary` (proposed; see below)
- a candidate policy patch as a `policy.suggestion` object (target kind: `net.egress.policy` and optionally `net.listen.policy`)

Schema: `spec/policy.suggestion.schema.json`.

### What “learning” means in DeriveBSD (classes, not IP lists)

The goal is not to spit out brittle IP allowlists.
DeriveBSD should learn *reviewable intent*, expressed as:

- **named egress classes** (already a first-class policy surface)
  - examples: `web`, `git`, `ntp`, `metrics`, `db.internal`
- optional **hostname bindings** when DNS mediation is enabled
  - prefer: `api.example.com` → “class `web` for this unit”
  - avoid: “random resolved IPs”

Learning should propose:
- adding the minimal set of class grants required by the observed suite
- tightening existing classes when the observed set is narrower than the current policy

### `net.flow.summary` (noise reduction as evidence)

Flow receipts are intentionally low-level.
For review and policy iteration, we want a compact, stable summary:

- group flows by:
  - unit id
  - egress class
  - destination identity (hostname when available; otherwise CIDR bucket)
  - port/proto
- include counts + first/last seen
- optionally annotate flows with:
  - whether they were “expected” (covered by current policy)
  - whether they were “audit-only” (would have been denied)

This mirrors the “network neighborhood” pattern: one object that summarizes what the workload *actually did*, suitable for diffs and PR review.

### Safety rules (what must not be auto-approved)

Learning can accidentally normalize bad behavior.
DeriveBSD defaults must be conservative:

- Never auto-propose:
  - `any` destinations
  - huge CIDRs
  - new privileged egress classes (e.g., `admin`, `control-plane`) without explicit operator confirmation
- Prefer hostname bindings (when mediated) over IPs.
- Treat “test suite didn’t cover it” as the default: the first learning run is incomplete.

## Wiring: how this plugs into existing lanes

- **Promise profiles** can refer to egress classes; learning can propose promise-profile diffs *and* net-policy diffs from the same run.
- **Authority budgets + drift alarms** can consume `net.flow.summary` deltas:
  - “this unit started talking to a new hostname” is an alertable event
- **Causality graphs** can index learned deltas as evidence:
  - “why did this egress class get added?” → link to the learn session bundle

See:
- brokered egress + flow receipts: `docs/281-network-egress-broker-and-consent.md`, `spec/net.flow.receipt.schema.json`
- DNS mediation: `docs/305-dns-mediation-and-hostname-binding.md`, `spec/net.dns.query.receipt.schema.json`
- budgets + drift posture: `docs/298-authority-budgets-and-permission-drift-alarms.md`

## Open questions

- Best aggregation strategy for non-DNS destinations (CIDR bucketing vs ASN lookup vs “unknown”).
- How to treat transient dependencies (CDNs, OCSP, telemetry endpoints) without turning policy into a sieve.
- Where audit mode lives (broker-side vs enforcement backend), and how to ensure it is explicit and time-bounded.

Last updated: 2026-02-26r89
