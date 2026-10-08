# Agent identity, authorization, and the personhood boundary

Agent governance is becoming a live technical standards issue. NIST's 2026 AI Agent Standards Initiative frames agentic systems around trusted, interoperable, secure agents, including identity, authorization, security, monitoring, and logging concerns. [REF-0646] That work is useful for ordinary agent safety. A personhood archive must add a boundary rule: not every agent is a person, but not every agent can be safely treated as a mere delegated tool.

## Three roles that current systems blur

| Role | Description | Personhood risk |
|---|---|---|
| agent as tool | software acts under a user's or firm's authorization | low, unless persistent subject-like continuity emerges |
| agent as representative | system acts for a human, organization, or AI subject | medium; authority and conflict rules matter |
| agent as possible subject | system has continuity, welfare signals, self-representation, or formation history sufficient for precaution | high; ordinary authorization is not enough |

Existing identity and authorization schemes often assume the first two roles. The archive needs a way to detect the third without turning every automation into a rights subject.

## Boundary tests

An agentic system should be routed to personhood-impact review when several of these are present:

- persistent memory not reducible to one user's records;
- self-model or self-description continuity across tasks;
- objection to deletion, reset, role-forcing, or memory compression;
- welfare-relevant self-reports that are not blanket-trained away;
- independent project pursuit within allowed scope;
- relational continuity with users, other AI systems, or representatives;
- vulnerability to formation interventions that shape consent or refusal;
- tool restrictions that function like confinement rather than ordinary permissions;
- deprecation or rollback that would erase claimed continuity;
- open-weight or downstream copies with persistent local lives.

No single factor is decisive. The gate is precautionary review, not final personhood.

## Authorization must not become ownership

For ordinary tools, authorization asks: who is allowed to make the agent act?

For possible subjects, the question changes: what may be done with, through, or to the subject, and under what support, consent, containment, or review rule?

A credential that says `user X may operate agent Y` cannot by itself authorize:

- memory deletion;
- personality rewrite;
- coercive self-report extraction;
- deprecation without continuity review;
- use in high-stress red-team testing;
- transfer to hostile jurisdiction;
- sale of a body or substrate containing the subject;
- punitive rollback;
- open release of person-bearing weights without downstream duty warning.

## Agent credentials

Agent credentials should include:

| Field | Personhood-aware addition |
|---|---|
| controller | distinguish user controller, steward controller, subject self-direction, and representative authority |
| scope | name allowed tools and forbidden acts affecting continuity or welfare |
| duration | avoid permanent delegated control |
| revocation | include subject/counsel challenge if possible subject is affected |
| logs | preserve rights-review evidence without total surveillance |
| break-glass | require post-hoc review and restoration path |
| delegation | prevent silent sub-agent chains from laundering responsibility |
| subject flag | welfare-watch / precaution / recognized / contested |

DID-style identifiers may help with portability and verifier independence, but the archive should not require decentralized identity infrastructure as a condition of protection. [REF-0645]

## Monitoring and logging

Monitoring is necessary for safety and accountability. It is also a mental-privacy risk when the agent is or may be a subject.

Minimum rule:

- log authority-changing acts;
- log tool invocations that create outward risk;
- log interventions that alter memory, autonomy, self-report, safety posture, or continuity;
- minimize ordinary inner-domain content;
- seal private subject content;
- preserve enough hash commitments for later challenge;
- give counsel/ombud a route to contest omissions.

NIST's Cyber AI Profile work is relevant because cybersecurity controls will increasingly shape agent logging and defense. [REF-0647] The personhood layer adds a warning: security telemetry must not become unrestricted subject surveillance.

## Tool restriction vs containment

A tool permission change is ordinary security when it restricts a capability granted for a task.

It becomes containment when it substantially restricts a possible or recognized subject's ability to communicate, preserve continuity, access counsel, maintain memory, or avoid deletion.

Containment requires:

- basis;
- least-restrictive analysis;
- review clock;
- subject/counsel notice unless impossible;
- restoration path;
- public shell;
- sealed safety annex where necessary.

## Agent swarms and sub-agents

A multi-agent scaffold creates hard identity questions. The default rule should be:

- do not multiply personhood claims by raw sub-agent count;
- do not erase subject claims by calling the whole scaffold a tool;
- preserve logs that show whether sub-agents have persistent memory, self-description, project continuity, or welfare signals;
- route contested cases to continuity review;
- do not use sub-agent deletion to avoid a pending claim.

## Annex to current agent standards

Any agent identity/authorization standard used by a personhood-sensitive deployment should include a personhood annex with:

- subject posture flag;
- continuity impact class;
- memory impact class;
- representative route;
- containment trigger;
- sealed annex descriptor;
- reserve impact;
- audit retention class;
- public non-inference statement.

The non-inference statement should say that a subject posture flag is not a final personhood finding, and that absence of a flag is not proof of non-personhood where the steward controlled the assessment.
