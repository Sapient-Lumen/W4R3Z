# 901 — Identity credential access and delegated authority dockets: assurance levels, recovery, relying-party boundaries, and no public service by login

## One-line thesis

Public digital identity is an access waist, not the right itself: a login, proofing score, assurance level, passkey, biometric check, wallet credential, or delegated mandate must be treated as evidence for a bounded service action, not as entitlement, eligibility, consent, agency, or lawful denial.

## Why this matters

The archive already distinguishes identity, mandate, and delegated authority in `406`, and it has tested status-proof migration in `889`. But public-service identity systems are becoming a more general chokepoint. A single account can sit in front of tax records, benefit claims, corporate filings, immigration proof, student aid, public procurement, health services, professional authorisations, and casework portals. That account may be operated by the state, a shared service, a private identity provider, a credential service provider, a wallet issuer, or a hybrid supplier stack.

This can be good governance. Reusable credentials can reduce password sprawl, prevent fraud, improve auditability, and spare people from proving the same fact repeatedly. It can also become public-law theater. A user who fails remote proofing may be treated as if they lack the underlying right. A person with a valid legal status may be locked behind recovery friction. A representative may be forced into unsafe password sharing because the service cannot model delegated authority. A service may cite standards compliance without showing which assurance level the actual transaction needs. A common identity front door can silently move risk from a department to a central platform while the department still owns the public service.

The honest form is a credential-access docket. It does not ask whether identity is useful in general. It asks whether the proofing, authentication, federation, delegated-authority, recovery, privacy, supplier, relying-party, outage, and fallback controls match the public consequence of the transaction.

## Pattern pack

### 1. Separate person, credential, account, session, mandate, and entitlement

A public service should keep these states distinct:

| State | What it proves | What it does not prove |
| --- | --- | --- |
| person | a human or entity claim has been bound to evidence | eligibility, authority, consent, or current legal status |
| credential | a credential service has issued or accepted a proof route | that every relying service should use it for every transaction |
| account | a user can access a profile or session | entitlement to the underlying benefit, refund, service, or status |
| session | a current authentication event occurred | that the user can take all possible actions |
| mandate | someone may act for another person or entity | that the delegate may exceed the granted scope |
| entitlement | the law or programme says the person has a right or claim | that identity proofing will always display it correctly |

The first docket question is whether the proposal collapses any of these states.

### 2. Assurance level is a transaction decision

Identity assurance should be risk-matched. A low-risk information service, a tax-record transcript, a business filing, a benefit application, a payment instruction, a child record, and a legal representative action may need different identity, authentication, and federation controls. A platform should not force the highest-friction route for every transaction merely because it can; it also should not cite a general assurance claim when a high-risk action needs stronger proof.

The docket must name:

- relying service;
- transaction class;
- required identity assurance;
- required authenticator assurance;
- required federation assurance;
- fallback route;
- delegated or representative route;
- evidence that the route meets the current standard or documented local equivalent.

### 3. Proofing failure is not substantive ineligibility

A failed remote proofing attempt, inaccessible phone, unavailable passport journey, credit-file mismatch, facial-comparison failure, account lock, passkey loss, or vendor support ticket should not be treated as a merits decision. It is an access failure unless the service produces a separate eligibility, fraud, sanction, or legal-effect docket.

When a person cannot pass the primary route, the service should preserve:

- assisted digital support;
- in-person proofing where proportionate;
- paper, phone, mail, or appointment fallback where necessary;
- urgent continuity for payments, deadlines, travel, healthcare, housing, or legal rights;
- reviewable reasons for denial or account lock;
- a way to correct identity attributes without losing the underlying claim.

### 4. Delegation is not password sharing

A competent identity system must model representation. Parents, guardians, executors, attorneys, tax professionals, corporate officers, carers, public servants, caseworkers, and contractors need role-limited authority. If the service only knows a personal account, users will improvise through shared passwords, screenshots, unofficial staff overrides, and informal family control.

A mandate credential should name the delegator, delegate, scope, expiry, revocation path, relying services, action classes, and audit record. It should not fuse the delegate's whole life with the principal's account.

### 5. Relying-party obligations stay live

A shared identity provider does not own the whole service. Each relying department, agency, regulator, or service owner must still justify why it needs proof, what assurance level it selected, what user groups are excluded, how it handles delegated authority, how it supports account recovery, and what happens when the identity platform fails.

The identity platform should publish platform-level evidence. Relying services should publish service-level evidence.

### 6. Standards claims need dated proof

Identity standards change. Programmes upgrade. Independent certifications expire. Assurance claims can be overbroad. A docket must separate:

- standard named;
- version or revision;
- scope of certification or assessment;
- service offering covered;
- transaction classes covered;
- known exclusions;
- transition plan when standards change;
- independent audit, certification, or public status record.

No public service should rely on a stale assurance slogan.

### 7. Privacy and biometric boundaries are public-law controls

Proofing may involve document images, address history, credit-bureau data, device signals, selfies, videos, face comparison, fraud scores, liveness checks, and third-party providers. These are not merely security details. They determine who can access public services and what evidence the state or its supplier collects about them.

The docket should ask:

- what data is collected;
- who receives it;
- how long it is retained;
- whether biometric data is used;
- whether a non-biometric route exists;
- whether records are reused across services;
- what the person can inspect, correct, delete, or contest;
- what happens on suspected fraud.

### 8. Recovery is part of access

A credential system is not reliable if it works only for users who keep the same device, phone number, email address, identity documents, name, address, disability status, and life circumstances forever. Recovery routes should be designed for lost phones, expired documents, name changes, homelessness, incarceration, domestic abuse, overseas residence, disability, bereavement, guardianship, language barriers, and low digital access.

The recovery docket is as important as the enrollment docket.

### 9. Outage and maintenance are rights-access events when high-stakes services depend on the credential

When a shared identity service is down, a user may miss a filing, fail to prove status, lose an appointment, be unable to view a notice, fail to authorize a representative, or lose time-sensitive payment control. Status pages and scheduled maintenance notices are useful, but they are not sufficient.

The service should name emergency alternatives, deadline protection, incident thresholds, affected services, affected user groups, and post-incident learning.

### 10. The credential access docket

A credential-access docket passes only when it includes:

1. service action and consequence class;
2. legal owner and relying-service owner;
3. identity, authenticator, and federation assurance level;
4. proofing route list and inclusion evidence;
5. delegated-authority route;
6. account recovery and attribute correction route;
7. privacy, biometric, supplier, and retention boundary;
8. outage, maintenance, deadline, and fallback route;
9. public metrics for proofing success, lockouts, recovery, accessibility, and complaints;
10. standards reapproval and material-change clock.

## Failure modes

- **login-right fusion**: account access is treated as the right.
- **proofing-ineligibility fusion**: identity-proofing failure is treated as substantive denial.
- **assurance slogan theater**: the platform cites compliance without dated scope, standard version, or transaction fit.
- **private credential capture**: a supplier or credential provider becomes the practical gate to public service without public-owner records.
- **representative erasure**: carers, representatives, tax professionals, guardians, corporate officers, and attorneys are forced into unsafe workarounds.
- **recovery cliff**: the service works until a person loses a device, changes a number, moves, ages, becomes disabled, or changes name.
- **biometric coercion by convenience**: the nominally optional non-biometric route is too slow, inaccessible, or hidden to be real.
- **single-front-door brittleness**: central sign-in outage or maintenance defeats many services at once.
- **relying-party abdication**: departments blame the identity platform for access failure while still owning the service consequence.
- **standards drift**: a programme keeps relying on an old assurance representation after standards, certification scope, or service configuration change.

## Anti-theater tests

This note fails if the archive accepts "secure login," "one account," "verified identity," "IAL2," "single sign-on," "facial match," "passkey," "wallet," or "government identity" as enough. It passes only when the service-specific consequence, assurance fit, delegated authority, fallback, recovery, supplier boundary, privacy boundary, outage route, and standards-currentness record are visible.

## Holding

The rule is: **no public service by login**. A digital credential may be necessary evidence, but it is not the entitlement, the mandate, the public-service duty, or the lawful denial. Every high-stakes identity gate needs a credential-access docket before the archive credits it as secure, inclusive, or legitimate.
