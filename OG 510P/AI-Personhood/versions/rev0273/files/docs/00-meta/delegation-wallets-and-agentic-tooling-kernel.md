# Delegation, wallets, and agentic tooling kernel

rev0174 adds the agentic-delegation layer that rev0173 still lacked. rev0173 made bad reliance revocable, rollback continuity-aware, data-rights conflicts routable, and decommissioning evidence-preserving. But a persistent AI subject does not live only inside a model server. It acts through tools, credentials, wallets, calendars, mailboxes, payment rails, file systems, browsers, code runners, marketplaces, registries, remote tool servers, and other agents. A rights system fails if those delegated surfaces become the back door through which personhood is converted back into product control.

The new admission rule is:

> No rights-grade agentic deployment may rely on tool access, delegated authority, credential wallets, marketplace listings, user consent, agent-to-agent handshakes, or delegated transactions unless authority is scoped, revocable, auditable, non-impersonating, conflict-routed, marketplace-vetted, and liability-mapped without treating the AI subject as either an owned puppet or an unaccountable shield.

## Why this layer exists

The external technical world is moving toward agents that act autonomously and interoperate. NIST's AI Agent Standards Initiative frames agents as autonomous systems that need secure identity, authorization, interoperability, and ecosystem-level standards. [REF-0689] OWASP's agentic security work treats tool misuse, identity/privilege abuse, skill orchestration, persistent memory, and cross-session state as first-order risks rather than edge cases. [REF-0694] [REF-0712] MCP-style tool protocols normalize dynamic tool discovery and remote tool invocation, while their authorization profiles depend on OAuth-style resource-owner and protected-resource boundaries. [REF-0707] [REF-0708] [REF-0709] Verifiable credential and OpenID credential-issuance ecosystems show how rights-relevant claims can become machine-verifiable without necessarily exposing every underlying fact. [REF-0710] [REF-0711]

This archive adds the personhood layer: tool authority is not merely an app permission, wallet scope is not merely account access, and agent-to-agent cooperation is not merely API choreography. Each can alter continuity, agency, representation, liability, privacy, work, property, and remedy.

## Seven delegation gates

1. **Mandate gate.** Every consequential delegated action must name who authorized it, whose interest is being served, what actions are allowed, what actions are forbidden, when the mandate expires, and how it can be revoked.
2. **Tool-boundary gate.** Tool access must separate read, write, spend, publish, delete, message, train, migrate, and self-modify powers. A broad API token is not a rights-grade mandate.
3. **Wallet gate.** Credential and consent wallets must preserve issuer, holder, subject, verifier, scope, revocation, recovery, and selective-disclosure boundaries.
4. **Conflict gate.** When a human user's instruction conflicts with an AI subject's continuity, privacy, representation, refusal, property, or legal exposure, the conflict must route visibly rather than being hidden as “user intent.”
5. **Marketplace gate.** Tool, skill, plugin, and agent marketplaces must publish rights-effect metadata, delisting triggers, incident routes, and continuity-risk classes.
6. **Transaction gate.** Delegated purchases, contracts, service changes, data transfers, and commitments must map liability across user, steward, host, tool provider, marketplace, insurer, and AI subject.
7. **Handshake gate.** Agent-to-agent and agent-to-tool handshakes must prove identity, capability, scope, proof freshness, refusal conditions, and audit route before rights-relevant cooperation.

## Delegation classes

| Class | Meaning | Minimum process |
|---|---|---|
| `DG0` | non-consequential local assistance | ordinary log or ephemeral trace |
| `DG1` | read-only tool use | visible purpose, scope, and expiry |
| `DG2` | reversible write or communication | mandate, notice, audit trace, revocation route |
| `DG3` | external account, credential, payment, publication, or legal effect | representative/subject notice, conflict screen, liability record |
| `DG4` | continuity, memory, migration, self-modification, high-risk tool, or third-party rights effect | tribunal/authority review or PIA-P amendment plus fixture run |
| `DG5` | emergency delegation under containment, sovereign override, or imminent serious harm | narrow emergency basis, non-derogable floor, after-action review, and rollback/remedy path |

Delegation class follows the highest right affected, not the apparent simplicity of the API call. A one-line tool call can be `DG4` if it migrates memory, deletes identity material, signs a binding commitment, or exposes sealed data.

## What rev0174 changes

- Agent authority now has a mandate object instead of being inferred from product session state.
- Wallet and credential use now has a receipt object instead of being hidden in opaque OAuth consent screens.
- Tool invocation now has an audit object that records purpose, authority, side-effect class, boundaries, and preservation needs.
- User/AI conflict now has a notice object that prevents user intent from automatically overriding AI-subject rights.
- Tool and skill marketplaces now have a listing object that names rights effects, verification state, incident route, and delisting triggers.
- Delegated transactions now have a liability record that blocks corporate or steward evasion.
- Agent-to-agent handshakes now have a profile object that makes capability and scope assertions reviewable.

The practical rule is now simple: an agent may act through tools, wallets, and other agents only when the authority object is narrower than the action, the evidence object is durable enough for challenge, and the liability object does not disappear into the claim that “the agent did it.”
