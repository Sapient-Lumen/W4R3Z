# Rematch worlds should publish agent topology, memory, messaging, and authority as a world contract

Once a benchmark or rematch world contains multiple coordinated agents, outcomes depend not only on payoffs and policies but also on **who can talk to whom**, **what memory is shared or private**, **what message schema is allowed**, and **which roles can commit external actions or escalate decisions**.
If those fields are hidden in orchestration code, an inheritor can mistake a change in system wiring for a change in reciprocity, competence, or institution quality.

Recent external work reinforces this framing.
`RS-GR-045` emphasizes that multi-agent systems require explicit communication contracts, shared-context design choices, and authority / escalation models rather than leaving those choices implicit in runtime scaffolding.
For Concord, the compact lesson is that once a world uses role-specialized multi-agent coordination, the coordination graph itself becomes part of the institution/world contract.

## Minimum contract

If a world routes decisions through multiple agents, publish at least:

1. the **agent topology / role graph** (supervisor-worker, peer network, hub-and-spoke, declared DAG, or equivalent),
2. the **messaging contract** (free-form NL, structured fields, allowed message types, and any turn / bandwidth limits),
3. the **memory regime** (private scratch, shared board, durable cross-match memory, and reset rules),
4. the **authority graph** (which roles may call tools, commit actions, veto, suspend, or escalate),
5. and the **audit commitment** that records message flow, memory reads/writes, and action provenance at the level needed to replay institutional decisions.

## Implementor consequence

Do not compare two multi-agent rematch worlds as if they share one institution when one changes the communication graph, shared-memory policy, or action authority.
That is a world-contract change, not merely an implementation detail.

## Archive consequence

Keep this compact.
Prefer one retained coordination-contract note or receipt field over another bulky multi-agent orchestration report pair.
