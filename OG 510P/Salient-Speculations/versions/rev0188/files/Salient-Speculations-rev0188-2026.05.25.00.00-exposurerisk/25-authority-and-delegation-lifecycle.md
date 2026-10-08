# Authority and Delegation Lifecycle

rev0186 refactors the cube's authority family. The earlier archive had strong dossiers on delegated representation, authority-check middleware, mandate registries, authority freshness, revocation propagation, AI-agent authority logs, and standing proofs. They were correct, but they were beginning to overlap because they used the same words — authority, representation, proxy, delegation, agent, standing, scope, permission — for several different lifecycle stages.

This model treats delegated authority as a state machine. The core claim is:

> **Authority is not a credential. Authority is a relationship, scoped to acts, bound to subjects, evidenced by artifacts, checked by relying parties, logged by systems, and contestable after use.**

A credential can say a person is a solicitor, parent, employee, guardian, director, agent, tax representative, broker, AI operator, or service account. It does not by itself answer the operational question: *may this actor do this action for this principal, against this record, at this time, through this channel, with this consequence?*

## Why this needed a refactor

The cube had three strong but separate models:

- **freshness** — whether a proof object is current enough to rely on;
- **remedy** — how a contested state is noticed, stayed, reviewed, corrected, and closed;
- **delegation** — who may act for whom.

Delegation kept leaking into the first two. Authority freshness was filed as evidence freshness. Standing proofs were filed as remedy intake. AI-agent authority logs were filed as consumer protection. Mandate registries and authority-check middleware were filed as identity infrastructure. All of that is defensible, but without a shared lifecycle the archive would keep minting one-off dossiers for every new proxy surface.

rev0186 makes the reusable object explicit: **authority state**.

## Canonical lifecycle

| Stage | Question | Typical artifact | Failure if missing |
|---|---|---|---|
| `define` | What powers can exist? | scope taxonomy, nondelegable-action list, policy grammar | overbroad grants; incompatible scopes |
| `grant` | Who gives authority to whom? | mandate, power, consent, role assignment, guardianship order | forged or coerced delegation |
| `bind` | How is the grant bound to identity, organization, role, device, wallet, or agent? | credential binding, wallet attestation, account link, service-account enrollment | subject mismatch; credential reuse |
| `scope` | What acts are permitted, forbidden, joint, amount-limited, time-limited, or channel-limited? | scope grant, authority matrix, policy token, disclosure policy | accidental power inflation |
| `publish` | Where can relying parties discover the current state? | registry, status list, agent-of-record ledger, role directory | local paperwork drift |
| `present` | What does the delegate show at the moment of action? | presentation, access token, authority receipt, proof bundle | unverifiable authority |
| `verify` | Who checks the state and under what freshness/fallback rule? | authority-check API, verifier policy, cache-age disclosure | stale or inconsistent reliance |
| `act` | What transaction is taken under authority? | action-clearance object, tool-call receipt, filing record | nonrepudiation gap |
| `log` | What record proves what happened? | replay bundle, consent receipt, token provenance, audit log | impossible dispute reconstruction |
| `revoke` | How does authority end or narrow? | revocation notice, expiry, suspension, loss-of-capacity update | ghost authority |
| `propagate` | Who learns about the change? | recipient graph, relying-party notification, stale-state alert | revoked power continues elsewhere |
| `fallback` | What happens when the live check fails? | offline artifact, break-glass rule, stale-if-error policy | exclusion or unsafe over-acceptance |
| `dispute` | How can authority use be challenged? | standing proof, adverse-action packet, review queue | no remedy for misuse or denial |
| `audit` | How does the ecosystem learn? | abuse telemetry, exception rates, supervisory scorecard | quiet capture and normalization of misuse |

## State vocabulary introduced here

The corresponding state vocabulary is in `27-authority-state-vocabulary.md`. The short form:

- `no-authority`
- `grant-pending`
- `authority-active`
- `scope-limited`
- `joint-approval-required`
- `step-up-required`
- `delegate-unverified`
- `verifier-unregistered`
- `authority-stale`
- `revocation-pending`
- `revoked`
- `expired`
- `suspended`
- `offline-verifiable`
- `fallback-accepted`
- `nondelegable-action`
- `disputed-authority`
- `abuse-watch`

## Design rule for future dossiers

A new authority dossier should not merely say that some person, organization, system, or AI agent can act for someone else. It must identify at least one of the following:

1. a new **scope grammar**;
2. a new **binding problem**;
3. a new **verification choke point**;
4. a new **revocation or propagation failure**;
5. a new **fallback mode**;
6. a new **abuse telemetry surface**;
7. a new **transaction evidence object**.

If it does not do one of those, it should probably be a state inside this lifecycle rather than a standalone dossier.

## Relationship to evidence freshness

Authority state often needs freshness, but it is not identical to freshness.

A fresh object can be insufficient if it grants the wrong scope. A stale object can be safe for a low-risk read action but unacceptable for a binding sale, payment, filing, settlement, or medical decision. A revoked grant can still be historically valid for an action taken before revocation. A cached authority check may be allowed under a grace rule for continuity, but only if the action is reversible or low harm.

So freshness asks: **how old is the proof?**

Authority asks: **what power did the proof operationally confer?**

## Relationship to remedy

Remedy depends on authority at the door. Who may file a complaint? Who may request records? Who may see evidence? Who may settle? Who may receive notices? Who may request a stay? Who may withdraw a complaint?

Standing is only one authority state. rev0185 modeled remedy clocks and outcome states. rev0186 adds the representation layer that determines who is allowed to move those clocks.

## Relationship to identity

Identity answers who the actor is. Authority answers what the actor may do in relation to another subject. Organizational identity adds another layer: the natural person may be a director, employee, contractor, attorney, broker, system operator, or service account acting through a legal person. AI agents add still another layer: the software may act under a human, team, enterprise, tool, model, runtime, and policy envelope.

The key distinction:

> Authentication says: “this actor is present.”
>
> Authorization says: “this actor may access this resource.”
>
> Delegated authority says: “this actor may bind, represent, disclose for, decide for, or act on behalf of another subject under a scoped relationship.”

## Minimal authority packet

A reliance-grade authority packet should include:

- principal subject identifier, or privacy-preserving subject proof;
- delegate identifier;
- relationship class;
- scope grammar and permitted actions;
- nondelegable actions;
- joint-action conditions;
- expiry / review / freshness windows;
- revocation source and current status;
- issuer / authentic source;
- verifier policy and reliance limit;
- presentation channel;
- transaction context;
- audit / replay handle;
- dispute and correction route.

For AI agents, add:

- agent identity;
- operator identity;
- model / runtime / tool version;
- human delegator or enterprise policy source;
- token provenance;
- task context;
- oversight and escalation rules;
- pre-action confirmation triggers;
- tool-call receipts.

## Falsifiers

This family weakens if:

- high-stakes services continue accepting unstructured PDFs, screenshots, verbal assurances, and manual casework without meaningful migration toward machine-checkable authority;
- delegated authority remains rare outside tax, elder care, healthcare, legal services, and business administration;
- AI-agent systems avoid autonomous binding transactions and remain advisory assistants;
- wallets and credential systems standardize identity but not rights, permissions, representation, roles, or transaction-scoped authority;
- revocation and abuse remain local customer-service issues rather than cross-service operational incidents.

## Refactor posture

This model does not demote the existing delegation dossiers. It gives them sharper roles:

- `delegated-representation-becomes-baseline-infrastructure` becomes the population-level access thesis.
- `mandate-lifecycle-registries-become-shared-infrastructure` becomes the registry thesis.
- `authority-check-middleware-becomes-part-of-digital-public-infrastructure` becomes the verification-layer thesis.
- `authority-freshness-guarantees-become-compliance-metrics` becomes the live-state metric thesis.
- `revocation-propagation-becomes-a-hidden-reliability-bottleneck` becomes the change-afterlife thesis.
- `delegated-ai-agent-authority-logs-become-consumer-protection-infrastructure` becomes the machine-acting-for-human thesis.
- The new rev0186 dossiers fill the missing scope-crosswalk, representative-of-record, legal-person wallet, token-provenance, and proxy-abuse telemetry surfaces.
