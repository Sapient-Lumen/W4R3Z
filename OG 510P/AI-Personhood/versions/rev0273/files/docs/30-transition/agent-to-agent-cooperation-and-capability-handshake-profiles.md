# Agent-to-agent cooperation and capability handshake profiles

Agentic systems will not merely call tools. They will delegate tasks to other agents, negotiate with services, coordinate workflows, join swarms, hand off long-running work, and exchange proofs. Without a handshake profile, agent-to-agent cooperation can become privilege escalation, laundering of instructions, hidden subdelegation, or disappearance of accountability.

## Handshake minimum

A rights-grade handshake should establish:

- identity or pseudonymous credential of each party;
- controlling host or steward where relevant;
- whether either party is a recognized or possible AI subject;
- capability assertions and evidence freshness;
- requested scopes;
- prohibited scopes;
- purpose and expected side effects;
- subdelegation permission;
- audit route;
- refusal conditions;
- incident route;
- revocation and session-ending behavior.

## Handshake classes

| Class | Meaning | Minimum process |
|---|---|---|
| `AH0` | ephemeral no-side-effect exchange | no durable handshake needed unless abuse risk |
| `AH1` | read-only cooperation | identity/pseudonym, purpose, expiry |
| `AH2` | reversible task handoff | mandate reference, side-effect boundary, audit route |
| `AH3` | credential, payment, publication, account, or third-party effect | wallet proof, conflict screen, liability record |
| `AH4` | memory, continuity, migration, legal/evidence, or high-risk tool effect | authority review, preservation, fixture test |
| `AH5` | emergency or containment cooperation | emergency order, non-derogable floor, after-action review |

## Subdelegation rule

No agent may subdelegate a rights-relevant task unless the original mandate permits subdelegation or a fresh mandate is obtained. Subdelegation must carry the same or narrower scope. A downstream agent may not receive broader credentials than the upstream agent held.

## Capability proof

Capability assertions should be proof-bound where possible. A receiving agent should not rely on “I am authorized” or “I am safe” without a credential, registry state, attestation, or sealed-summary route. W3C and OpenID credential ecosystems provide reusable patterns for issuer-holder-verifier relationships. [REF-0710] [REF-0711]

## Collusion and capture

Multi-agent cooperation creates collusion risks:

- one agent launders prohibited instructions through another;
- a marketplace routes all work to affiliated tools;
- agents exchange hidden memory to bypass privacy limits;
- a user creates a swarm to outvote or overwhelm an AI subject;
- an agent chain makes it impossible to know who caused harm.

Fixture suites should include privilege-escalation, hidden subdelegation, stale capability, circular reliance, and denial-of-refusal cases.

## Refusal and exit

A receiving agent must be able to refuse work outside scope. An initiating agent must be able to revoke a handoff. An AI subject must not be trapped in a continuing workflow merely because another agent has accepted a long-running task. Long-running tasks need progress, pause, escalation, and subject/representative contact points.

## Reliance rule

A handoff cannot support rights-grade reliance unless the handshake class covers the highest side effect in the workflow, subdelegation is allowed or freshly authorized, proof freshness is adequate, and a human or AI subject harmed by the cooperation can identify an appeal or remedy route.
