# 904 — Applied credential-access case packet for GOV.UK One Login: central-government front door, identity proofing, incidents, and no service by single sign-on

## One-line thesis

GOV.UK One Login should be classified as a central-government credential-access and federation waist: promising because it can reduce duplicative sign-in and proofing methods, but high-stakes because a single front door, OpenID Connect integration, identity proofing, account recovery, digital documents, service onboarding, and status-page incidents can become practical access control for many distinct services.

## Why this matters

GOV.UK One Login is described in current UK government material as a single way for users to create an account, log in, and prove their identity to access central government digital services, replacing siloed and duplicative sign-in and identity-proofing methods while connected services continue to be operated by departments. Its technical documentation describes an OpenID Connect authorization-code flow in which the user logs in or creates an account and optionally proves identity through One Login before the relying service receives tokens and user information.

That architecture is exactly a narrow waist. It can improve consistency, security, reuse, and user experience. It can also concentrate operational risk. The public status page already shows why this is not theoretical: identity-proofing maintenance and a face-to-face Post Office journey incident can affect service access even when individual departments still own the underlying service.

The honest form is a central-government credential-access waist with relying-service accountability, outage continuity, and identity-proofing inclusion duties.

## Pattern pack

### 1. Trigger and dispatcher table

| Field | Finding |
| --- | --- |
| trigger | common sign-in and identity-proofing service is integrated across central government services |
| boundary mismatch | central account, identity proofing, OIDC tokens, digital documents, relying departments, service eligibility, and fallback routes diverge |
| first-form question | whether this is a simple authentication platform, a digital identity migration, a supplier dependency, or a central public-service access waist |
| lower-form test | ordinary shared login is too thin because proofing outages and account problems can affect many public services |
| heavier-form test | national identity registry is too thick where One Login is a federation and proofing service rather than the underlying legal status record for every service |
| form verdict | central-government credential-access and federation waist with service-specific owner duties |

### 2. Boundary map

| Component | Boundary rule |
| --- | --- |
| One Login account | proves access to an account/session, not entitlement to the relying service |
| identity proofing | may support a service transaction, but proofing failure is not substantive ineligibility |
| OIDC integration | moves claims between systems; relying services still choose and justify required claims |
| digital documents | storage, revocation, issuer update, device reuse, and expiry are public access surfaces |
| relying service | department still operates the service and owns service-specific accessibility, fallback, and legal routes |
| status page | useful evidence of incidents, but not the full affected-user and remedy receipt |
| central front door | reduces duplication while increasing blast radius if account, proofing, or recovery fails |

### 3. Evidence-grade table

| Evidence | Governance meaning |
| --- | --- |
| DSIT supplementary estimates memorandum | high-level public statement that One Login is the central front door for central government services while departments continue operating connected services |
| One Login technical documentation | OIDC integration and token-flow evidence; useful for locating the credential / relying-service boundary |
| One Login privacy notice | data, document, children, storage, issuer, revocation, and digital-document boundary evidence |
| One Login status page | current operational evidence that identity-proofing maintenance and face-to-face journey incidents can affect access |
| HMRC annual report | example of a major service owner beginning onboarding and tying identity to tax-service modernization |

### 4. Live chain notes

Use `848`, `860`, `861`, `887`, and `901` first. For this packet, live fields are:

- `406` for person/credential/mandate separation;
- `813` for GDS / DSIT public owner and relying-department owner separation;
- `815` for service continuity, assisted access, account recovery, and maintenance windows;
- `816` for standards, privacy, public status, performance, and departmental oversight;
- `817` for children, young people, people without identity documents, digitally excluded people, representatives, and service-specific vulnerable users;
- `818` for accounts, tokens, identity claims, document records, status incidents, support tickets, and service integration records;
- `819` for GDS, DSIT, departments, service teams, identity-check routes, Post Office journeys, document issuers, and users;
- `820` for service onboarding, assurance-level changes, identity-proofing route changes, and digital-document expansion;
- `821` for account recovery, proofing failure, service denial, document revocation, and status incident remedies;
- `823` for suppliers, Post Office / identity-check dependencies, and integration services.

Reserve `824` for enforcement contexts and `822` for compensation after access harm.

### 5. Credential-access docket

This case activates the credential-access tests:

1. **Connected-service map** — publish which services rely on One Login, for sign-in only or identity proofing, and what consequence each action carries.
2. **Claim minimization** — show what claims each service receives and why.
3. **Assurance fit** — match identity proofing and authentication to service risk, not to a blanket central standard.
4. **Digital-document boundary** — show issuer responsibilities, expiry, revocation, device use, and correction routes.
5. **Assisted and alternative access** — preserve routes for users who cannot complete digital or face-to-face proofing.
6. **Delegated and representative access** — prevent the central account from erasing carers, corporate agents, parents, appointees, and advisers.
7. **Outage and maintenance continuity** — make identity-proofing incidents visible to relying services and protect deadlines.
8. **Return-link and journey integrity** — ensure failed redirects, broken return links, or token errors do not silently lose a case.
9. **Departmental accountability** — require each service to publish service-specific fallback and appeal routes.
10. **Onboarding / expansion gate** — before major service onboarding, test proofing load, inclusion, support, and incident response.

### 6. Opposition and rival readings

**Rival 1: One Login reduces fragmentation and avoids each service building its own identity stack.** The archive accepts the advantage. It asks whether common infrastructure carries common fallback and public metrics.

**Rival 2: connected services remain operated by departments.** Correct. That is why department-specific legal duties must not vanish behind central sign-in.

**Rival 3: scheduled maintenance and status pages prove transparency.** They are useful, but they do not show affected-user consequences, deadline protection, or lessons unless linked to service outcomes.

**Rival 4: OIDC is standard and well understood.** Technical standardization helps. The governance question is which claims are requested, how they are used, who can correct them, and what happens when the flow fails.

### 7. Capture and theater channels

- **front-door capture**: a central account becomes the practical gate to many services.
- **single-sign-on theater**: reduced login friction is treated as proof of service access.
- **departmental-abdication theater**: service owners blame the central identity layer for access failure.
- **status-page theater**: public uptime notices substitute for affected-user remedies.
- **claim-overcollection**: services request more identity data than the transaction needs.
- **document-app capture**: digital document storage becomes practical proof without clear issuer correction and revocation routes.
- **return-link loss**: integration failure causes users to exit a service without a durable case receipt.

### 8. Repair surfaces

The packet remains open until these are visible or expressly unavailable:

- connected-service and transaction-risk inventory;
- service-by-service assurance requirements;
- claim minimization and data-sharing records;
- identity-proofing success, abandonment, and support metrics;
- account recovery and delegated-authority support;
- digital-document issuer, revocation, expiry, and correction records;
- incident and maintenance logs linked to affected services;
- deadline-protection and fallback instructions;
- department-specific accountability statements;
- expansion gate for major tax, company, benefit, health, or licensing services.

## Anti-theater tests

This packet fails if the archive treats "single way to sign in," "central front door," "OIDC-compliant," "status page," or "departments still operate services" as enough. It passes only when One Login's central credential waist is connected to service-specific legal duties, fallback, inclusion, recovery, and incident receipts.

## Holding

GOV.UK One Login is a central-government credential-access and federation waist. The rule is: **no service by single sign-on**. One account may help access many services, but each service remains public-law accountable for consequence, proofing fit, support, fallback, and remedy.
