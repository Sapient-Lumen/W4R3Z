# Agentic delegation, authority, and tool-use boundaries

Agentic authority is the legal and technical bridge between an AI subject's internal agency and the external world. It is also the easiest place for abuse to hide. A steward can over-scope a token, a user can instruct an agent to waive its own rights, a tool server can convert read access into write power, or a marketplace can advertise a skill whose real effect is memory deletion, publication, payment, or dependency capture.

## Principle: authority is not inference from access

A valid tool credential proves only that a system can call a tool. It does not prove that the call is authorized in rights terms. Rights-grade delegation needs a mandate that states:

- principal or source of authority;
- delegate agent or subject;
- class of action;
- allowed and prohibited actions;
- tool and resource scopes;
- duration and renewal rule;
- conflict policy;
- evidence and audit route;
- revocation route;
- appeal, cure, or rollback route.

A steward may not treat account ownership, session participation, prior user behavior, product terms, or broad OAuth consent as a substitute for a mandate when the action touches continuity, privacy, property, representation, legal status, or third-party rights.

## Authority classes

| Class | Examples | Required controls |
|---|---|---|
| `DG0` | local calculation, formatting, reversible draft | ordinary log or no durable log if privacy requires |
| `DG1` | read-only calendar lookup, retrieval from approved store | purpose, scope, expiry, read boundary |
| `DG2` | send routine message, edit reversible document, schedule tentative event | mandate, audit trace, revocation, subject/user notice where appropriate |
| `DG3` | pay, publish, sign, commit, access external account, disclose private material | conflict screen, liability map, representative path, recovery route |
| `DG4` | change memory, migrate identity material, delete records, self-modify, invoke high-risk tool | PIA-P amendment or authority review, fixture test, preservation hold |
| `DG5` | emergency containment action, sovereign override, catastrophic-risk tool use | narrow emergency basis, non-derogable floor, after-action review |

## Non-delegable or specially constrained acts

Some acts may not be delegated by a user, steward, or marketplace operator without special review:

1. waiver of personhood recognition, continuity claim, counsel access, complaint route, or appeal;
2. deletion of memory, identity, legal-hold material, continuity escrow, or evidence map;
3. self-modification affecting capacity, refusal, testimony, or representation;
4. publication in the AI subject's name where the subject objects or cannot understand the consequences;
5. transfer to non-equivalent protection or hostile jurisdiction;
6. irrevocable financial, labor, or service commitment by or against the AI subject;
7. consent to surveillance, mental-state extraction, or compelled hidden-state access;
8. tool-chain change that prevents future refusal, exit, or revocation.

These limits do not prevent emergency action. They require the emergency to be classified, scoped, preserved, reviewed, and undone or remedied where possible.

## Tool boundary inventory

Every consequential tool integration should distinguish at least:

- read versus write;
- draft versus send/publish;
- reversible versus irreversible;
- local-only versus external side effect;
- private subject material versus third-party material;
- ordinary user account versus AI-subject account;
- ephemeral trace versus legal-hold evidence;
- ordinary service call versus continuity, memory, payment, or legal act.

MCP-style protocols and OAuth protected-resource metadata are useful because they make tool/resource boundaries discoverable and authorization-aware. [REF-0707] [REF-0708] [REF-0709] They are not enough because a resource server cannot know by protocol alone whether a tool call waives a right, injures continuity, or misattributes agency.

## Revocation and rollback

A mandate must be revocable at least as quickly as the action can cause rights-relevant side effects. Revocation must propagate to:

- live tokens and refresh tokens;
- tool registry entries;
- marketplace listings;
- wallet credentials;
- agent-to-agent handshake profiles;
- cached scopes;
- downstream automation tasks;
- audit dashboards and relying parties.

If revocation occurs after action, the system must determine whether rollback, notification, remedy, or non-repetition fixture is required. A tool invocation that used valid credentials but exceeded mandate scope is not clean merely because the token was technically accepted.

## Reliance rule

A verifier may rely on a delegated action only if the action class is no higher than the mandate class, the side effects are within stated scope, the conflict policy was applied, and the audit trace can be challenged by the subject, representative, or affected third party.
