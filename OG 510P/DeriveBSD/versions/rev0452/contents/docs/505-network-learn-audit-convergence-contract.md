# Network learn/audit convergence contract

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Observation→Suggestion→Review→Enforce, Broker→Lease→Receipt  

DeriveBSD already decided that outbound networking is brokered,
that DNS evidence posture is profile-shaped,
and that policy changes should land as reviewable artifacts instead of ambient clicks.

This doc locks the next expensive choice:
**network learning is a bounded convergence lane, not a standing permissive mode.**

See also:
- ADR: `adrs/ADR-0095-network-learn-audit-convergence-contract.md`
- learned network policy notes: `docs/328-learned-network-policies-from-flow-receipts.md`
- outbound posture baseline: `docs/459-outbound-network-posture-by-profile.md`
- DNS evidence posture: `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`
- consent/review UX: `docs/369-consent-ledgers-and-permission-review-ui.md`
- new summary artifact: `spec/net.flow.summary.schema.json`

## Why this needs a hard decision

Every least-network system rediscovers the same trap:
operators need a way to see real traffic before tightening policy,
but “observe first” quietly turns into **permanent allow-everything with logs** unless the lane is bounded.

DeriveBSD needs three things at once:

- source evidence (`net-flow-receipt`, optional `net-dns-query-receipt`),
- a compact review surface (`net-flow-summary`),
- and a clear statement that enforcement still comes from `net-egress-policy`, not from observation artifacts.

## Accepted baseline

Across all profiles:

- network learn/audit runs are **explicit named sessions**,
- every session is bounded by **time** and **event count**,
- `net-flow-summary` is the canonical compact evidence object for that session,
- `policy-suggestion` remains the reviewable proposed patch,
- `net-egress-policy` remains the authoritative enforced policy,
- and automatic promotion from learn evidence to enforcement is off by default.

That keeps “observe first” useful without turning it into a stealth ambient bypass.

## The canonical object split

| Object | Role | What it is not |
|---|---|---|
| `net-flow-receipt` | low-level broker evidence for attempted flows | not a stable review surface by itself |
| `net-dns-query-receipt` | optional brokered hostname-resolution provenance | not an ambient DNS tap |
| `net-flow-summary` | compact, bounded, evidence-only learning summary | not authority, not a packet capture |
| `policy-suggestion` | reviewable candidate patch | not enforcement by itself |
| `net-egress-policy` | authoritative reviewed egress policy | not auto-derived from logs |

This split is the important coherence move.
It keeps evidence, proposed changes, and actual authority from collapsing into one fuzzy “learning mode.”

## `net-flow-summary` as the canonical review surface

`net-flow-summary` exists so operators can review **what the workload consistently did during a bounded session** without reopening raw flow logs or packet traces.

It should summarize by stable review dimensions such as:

- subject,
- learned session id + bounds,
- egress class,
- destination identity (hostname when brokered DNS exists; otherwise bounded CIDR/service identity),
- port/protocol,
- counts + first/last seen,
- and policy view (`covered`, `audit-only-would-deny`, `adapter-gap`, etc.).

It is deliberately **evidence-only**.
The summary can justify a review,
but it does not grant the resulting authority.

## Product-shape defaults

| Profile | Default learn-session posture | Review posture for high-impact broadening | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `bounded-test-canary-incident-only` | `stronger-review-for-class-broadening-hostname-wildcards-cidr-broadening-and-dns-mediation-relaxation` | Fleet learning is useful, but it must stay bounded and cannot quietly widen service reach in prod. |
| **B workstation** | `trusted-ui-started-bounded-local-learning` | `review-required-silent-prompt-to-policy-promotion-forbidden` | A human may start a bounded troubleshooting run, but the result still lands as a reviewable suggestion rather than a hidden forever-allow rule. |
| **C general_os** | `bounded-learning-normal-for-derived-workloads-adapter-gaps-explicit` | `review-required-adapter-fallback-visible` | Learning helps converge policy for derived workloads while legacy escapes remain explicit adapters rather than pretending to be learned intent. |
| **D appliance_factory** | `maintenance-incident-lab-only-not-normal-production-posture` | `strong-review-default-for-any-broadening` | Production/factory systems do not run indefinite audit mode; learning is a controlled maintenance/incident tool. |

These are compiled consequences of existing network/evidence/export/approval posture,
not a new `product.profiles.defaults` key.

## What counts as “high-impact broadening” by default

The archive now treats these as stronger-review changes by default, especially in **A** and **D**:

- adding a broader or more privileged egress class,
- replacing a specific hostname with a wildcard or suffix glob,
- replacing a narrow CIDR or explicit service identity with a much broader CIDR,
- relaxing brokered-DNS requirements where hostname policy was previously the review surface,
- or proposing policy from adapter/fallback traffic while presenting it as governed broker traffic.

These are exactly the places where a convenient learning loop can otherwise hollow out the security model.

## What “bounded” means operationally

A learn/audit session should be answerable in one sentence:

- **who/what** was observed,
- **for how long**, with **how many events maximum**,
- under **which current policy digest**,
- and which evidence objects justify the suggested change.

That is why the summary object carries session metadata rather than burying bounds in CLI prose or support tickets.

## What remains open

This doc does **not** freeze:

- exact aggregation heuristics for every destination family,
- exact CLI syntax,
- exact quorum/approval numbers,
- or exact rendering details for review UI.

Those are implementation choices.
The hard part worth locking now is the contract:
**bounded session → evidence summary → reviewable suggestion → explicit enforcement**.

## Why this is worth locking now

This is a coherence move, not a new subsystem.
The archive already wanted learnable network policy;
this decision simply makes that lane precise enough to implement without backsliding into packet captures,
permanent audit mode, or invisible allow-rule creep.

Last updated: 2026-03-08r234
