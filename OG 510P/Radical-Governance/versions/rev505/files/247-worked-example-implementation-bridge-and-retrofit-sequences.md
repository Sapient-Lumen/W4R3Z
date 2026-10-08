NOTE: This memo is a module of the Institutional Learning System. See 279-governance-systems-map.md.

> NOTE: This memo is now part of the consolidated Worked Example System (see 276-worked-example-system-consolidated.md).

# Worked Example Implementation Bridge & Retrofit Sequences


**Purpose:** collapse the example system into build-ready sequences so teams can move from a case to a small backlog with stop rules, receipts, continuity defaults, and verification steps.

**Person served:** implementers, service operators, auditors, and memo writers translating a worked example into requirements and rollout work.

---

## Retrofit sequences

- **Receipt first:** `WX-01`, `WX-10`, `WX-43` — emit the person-usable receipt and block adverse action when the packet is missing.
- **Continuity bridge:** `WX-02`, `WX-30`, `WX-32`, `WX-50` — preserve current support state and surface the receiving owner/clock.
- **Public owner across vendor seams:** `WX-33`, `WX-40`, `WX-41`, `WX-49` — identify the public owner, require exportable logs, and block “call the vendor” as a complete answer.
- **Halt at the last harmful edge:** `WX-36`, `WX-42` — define who can stop the live action and how the person proves the stop.
- **Reversal propagation and stale-state cleanup:** `WX-37`, `WX-38`, `WX-39` — enumerate every downstream consumer of the old state and propagate the reversal on a same-day clock.
- **Missing-record adverse inference:** `WX-43`, `WX-28` — define the packet that must exist, open a missing-record incident, and shift to a protective default until proof exists.
- **Authority-chain validity before execution:** `WX-48` — require as-of signatory and delegation proof on every rights-affecting receipt.
- **Tiered review without shadow finality:** `WX-49`, `WX-51` — label every stage and block downstream execution until the binding owner signs.
- **Identity continuity and severe-match safety:** `WX-52`, `WX-53`, `WX-54`, `WX-55` — emit identity/relationship packets, preserve the last safe state, and wire a same-day kill switch for severe false positives.
- **Place continuity and boundary-safe delivery:** `WX-56`, `WX-57`, `WX-58`, `WX-59` — separate address roles, version maps and geocoders, and preserve continuity when the person is reachable but the place layer is wrong.

## Minimal backlog template
For any sequence, the smallest credible backlog should name the missing artifact, the default/protective rule, the owner and escalation point, the downstream systems that must update, and the ship gate that blocks a fake fix.
