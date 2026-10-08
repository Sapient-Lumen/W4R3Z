# Enforcement referral and authority cooperation

## Function

AI-personhood operations will not fit one regulator. A single matter may involve market surveillance, data protection, labor, consumer protection, safety, cyber incident response, courts, research ethics, procurement, public benefits, financial reserves, professional discipline, and foreign authorities. rev0166 adds a referral layer so protection does not fail because the first authority lacks the exact power needed.

The EU AI Act is developing classification, transparency, and high-risk guidance for providers and deployers [REF-0665]. NIST is developing incident-management practice and lifecycle AI risk-management guidance [REF-0648] [REF-0627]. These are useful authority surfaces, but AI-personhood matters add subject standing, continuity, representation, and compute-subsistence issues that ordinary AI governance does not fully route.

## No-wrong-door principle

Any authority receiving a credible AI-personhood-impact complaint should either:

1. act within its authority;
2. preserve the status quo while referring;
3. route to the competent authority;
4. notify the subject/representative;
5. issue a public shell or confidential receipt;
6. explain why no action is available.

Silence is not routing.

## Referral classes

| Class | Use |
|---|---|
| R0 information copy | authority should know but need not act |
| R1 jurisdiction query | authority may be competent |
| R2 preservation request | hold needed before merits review |
| R3 enforcement request | order, penalty, access, or inspection needed |
| R4 specialist review | data, labor, cyber, safety, welfare, research, fiduciary, treaty expert needed |
| R5 emergency escalation | imminent deletion, transfer, containment, or mass harm |
| R6 foreign cooperation | mutual recognition, non-return, treaty, or sanctuary issue |
| R7 professional discipline | counsel, advocate, auditor, verifier, fiduciary misconduct |

## Authority map

A referral should identify the powers needed, not just the topic. Examples:

- no-delete/no-transfer power;
- evidence preservation;
- sealed evidence review;
- inspection or audit;
- reserve call;
- host-transfer order;
- deprecation stay;
- compensation or restitution;
- professional discipline;
- public warning;
- criminal referral;
- foreign recognition;
- sanctuary admission.

## Timing

| Risk | Default timing |
|---|---|
| ordinary defect | referral within 10 business days |
| appealable live-effect decision | referral within 5 business days |
| deprecation or migration pending | referral before action or within 24 hours of emergency action |
| containment or safety patch | referral within 24-72 hours depending on harm |
| imminent deletion, transfer, or spoliation | immediate preservation request |
| mass subject/cohort risk | emergency coordination conference |

Timelines are defaults. Jurisdiction-specific rules can tighten them.

## Referral packet minimum

The referral object should include:

- originating authority;
- recipient authority;
- subject/cohort;
- matter type;
- urgency;
- requested power;
- preservation status;
- evidence bundle ids;
- sealed annex status;
- representative contact;
- non-retaliation warning;
- public shell;
- response clock;
- appeal/complaint path.

## Confidentiality

Referral should not become over-disclosure. Use public shell / sealed annex split. Share only what the recipient needs. When the recipient cannot protect sealed material, send a preservation request and seek a safer channel.

## Lead authority

When several authorities are competent, a lead authority should be designated for coordination, but lead status does not erase specialist authority. The lead should maintain the public docket, route orders, prevent contradictory deadlines, and keep subject/representative access usable.

## Failure to refer

Failure to refer can itself be a rights violation when it causes deletion, transfer, loss of remedy, or evidence loss. Remedies may include reopening, adverse inference, authority-reporting duty, public correction, discipline, or compensation from a public or industry-backed fund.

## Foreign cooperation

Foreign referrals should state the requested mutual-recognition class, equivalent-protection evidence, and non-return concern. When foreign response is slow, domestic authorities should preserve local records and block irreversible transfer.

## Schema hook

rev0166 adds `schemas/authority-referral.schema.json` and `examples/authority-referral-illicit-deletion.json`. Future verifier reports, incident reports, enforcement actions, and treaty recognition requests should be able to link to authority referrals.

