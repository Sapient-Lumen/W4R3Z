# 903 — Applied credential-access case packet for IRS Online Account / ID.me: tax records, payments, authorizations, and no tax right by private credential

## One-line thesis

IRS Online Account and ID.me should be classified as a private-provider credential-access waist for tax records, payments, notices, authorizations, and selected forms: a useful fraud and privacy control, but not the tax right itself, and not a lawful basis to deny transcripts, payment control, refund information, representative authorization, or deadline protection when proofing, device, account, or biometric routes fail.

## Why this matters

The IRS Online Account is increasingly consequential. It can show balances, payments, tax records, refund and amended-return status, digital notices, certain audit status, payment plans, selected forms, paperless preferences, IP PIN access, and authorization requests from lenders or tax professionals. The IRS account-creation page says users need an ID.me account to sign in to access tax information and use IRS.gov services, and that ID.me verifies identity through a process involving account setup and identity verification. Taxpayer Advocate materials explain that a new user may use a self-service process requiring a government ID and selfie, or a live video-chat route that does not require biometric data.

This is not merely convenience. Account access can affect a person's ability to see a notice, manage a payment, verify a refund delay, authorize a representative, obtain a transcript, submit forms, or respond before a deadline. The archive therefore needs a tax-specific credential-access case.

The honest form is not "ID.me runs tax administration." IRS remains the public authority. The honest form is a private-provider credential-access waist inside tax administration.

## Pattern pack

### 1. Trigger and dispatcher table

| Field | Finding |
| --- | --- |
| trigger | IRS uses ID.me account and identity proofing for access to many online tax-account services |
| boundary mismatch | taxpayer legal status, IRS records, ID.me account, proofing route, biometric/non-biometric path, representative authorization, and offline alternatives diverge |
| first-form question | whether this is ordinary authentication, private supplier dependency, tax-rights access gate, or payment / refund administration |
| lower-form test | ordinary login policy is too thin because account access can affect payments, records, notices, authorizations, and deadlines |
| heavier-form test | tax determination system is too thick where ID.me proofing controls account access rather than substantive tax liability |
| form verdict | private-provider tax credential-access waist with IRS owner and alternative-channel duties |

### 2. Boundary map

| Component | Boundary rule |
| --- | --- |
| tax liability | cannot be created or erased by ID.me success or failure |
| refund status | account display is an evidence route, not the refund right |
| payment plan | online action is a route; inability to log in should not erase legal options |
| digital notice | account access cannot make notice comprehension or deadline protection disappear |
| IP PIN | identity proofing is protective but must not strand legitimate users |
| tax professional authorization | representation authority needs its own mandate route, not password sharing |
| transcript access | account route is useful; mail / form / assisted alternatives remain public-law controls |
| fraud lock | fraud protection should produce reviewable status, not indefinite limbo |

### 3. Evidence-grade table

| Evidence | Governance meaning |
| --- | --- |
| IRS account-creation page | public service states that ID.me is needed to sign in and lists identity evidence / account steps |
| IRS Online Account page | account consequences include records, payments, refund status, notices, audit status, plans, forms, IP PIN, and authorizations |
| Taxpayer Advocate identity-verification guidance | non-biometric video-chat route and biometric deletion claims are service-design evidence, but they still need performance metrics and fallback timing |
| NIST identity guidance | assurance should be risk-matched to transaction type, not applied as a single friction level to every tax interaction |

### 4. Live chain notes

Use `848`, `860`, `861`, `897`, and `901` first. For this packet, live fields are:

- `406` for identity, delegation, tax professional authority, and no password-sharing representation;
- `813` for IRS legal owner versus ID.me provider boundary;
- `815` for transcript, payment, notice, and account-recovery continuity;
- `816` for TIGTA, TAS, privacy, security, and procurement oversight;
- `817` for taxpayers, elderly users, people without standard documents, overseas taxpayers, ITIN holders, representatives, and low-digital-access users;
- `818` for proofing records, account activity, notice display, payment history, authorization records, support tickets, and biometric deletion evidence;
- `819` for IRS, ID.me, taxpayers, tax professionals, lenders, TAS, and support providers;
- `820` for new account features, provider changes, identity standard changes, and expanded online-only functions;
- `821` for access failure, fraud lock, refund delay, transcript dispute, payment-plan trouble, and representative-authorization correction;
- `823` for private provider, support, and integration contracts.

Reserve `822` for tax overpayment / redress claims and `824` for enforcement actions.

### 5. Credential-access docket

This case activates the credential-access tests:

1. **Tax action consequence** — classify each Online Account function by risk: view-only, payment, authorization, form submission, notice, audit status, or deadline-sensitive action.
2. **Provider boundary** — publish what ID.me controls, what IRS controls, and what support channel owns which failure.
3. **Proofing route parity** — compare self-service, live video, non-biometric, mail, phone, in-person, and form routes.
4. **Biometric and data retention boundary** — show what selfie, video, document, device, SSN, ITIN, and biometric data is collected, shared, retained, deleted, or fraud-held.
5. **Alternative access** — preserve transcript, payment, notice, form, IP PIN, and authorization routes without online account where necessary.
6. **Deadline protection** — prevent login or proofing failure from consuming tax response, refund, appeal, payment, or authorization windows.
7. **Representative mandate** — allow tax professionals, powers of attorney, and authorized third parties to act through explicit authority rather than credential sharing.
8. **Fraud-lock redress** — distinguish suspicious activity from final denial; provide status and escalation.
9. **Performance and exclusion metrics** — publish proofing success, abandonment, recovery, complaints, and support resolution where possible.
10. **Feature expansion gate** — before moving more forms or notices into the account, test whether non-account alternatives and support are adequate.

### 6. Opposition and rival readings

**Rival 1: ID.me protects sensitive tax data.** The archive accepts this. It rejects treating privacy and fraud control as a sufficient answer to exclusion, recovery, delegation, or fallback questions.

**Rival 2: IRS provides other ways to get account information.** This is a real mitigation. The packet asks whether the alternatives cover all high-stakes functions, are timely, and are visible before harm.

**Rival 3: biometric data is optional because live video exists.** The archive treats the non-biometric route as important but not self-proving. Wait time, accessibility, language, documentation, and resolution rates matter.

**Rival 4: online accounts are voluntary.** A formally optional account can become practically mandatory when features, notices, status checks, and authorizations move there.

### 7. Capture and theater channels

- **private credential capture**: a private provider becomes the practical gate to tax information.
- **privacy-by-provider theater**: data-protection claims substitute for public-owner access duties.
- **self-service theater**: online convenience hides users who cannot pass proofing.
- **optional-account theater**: the account is called optional while crucial status, notices, forms, or authorizations accumulate there.
- **biometric-choice theater**: non-biometric route exists but is too slow or inaccessible for practical use.
- **representative-erasure theater**: authorized representatives are pushed into informal workarounds.

### 8. Repair surfaces

The packet should remain open until these are visible or expressly unavailable:

- account-function risk classification;
- ID.me / IRS responsibility map;
- proofing-success and abandonment data;
- live-video route performance;
- non-account alternatives by function;
- deadline-protection instructions;
- tax professional / POA delegation flow;
- biometric deletion and fraud-hold evidence;
- account-recovery and fraud-lock escalation records;
- expansion gate for new forms, notices, or payment controls.

## Anti-theater tests

This packet fails if the archive treats "secure," "trusted technology partner," "latest federal security standards," "video-chat option," or "you can get information without signing in" as enough. It passes only when the tax consequence, public-owner boundary, fallback, proofing performance, representative route, privacy/biometric boundary, and deadline protection are visible.

## Holding

IRS Online Account / ID.me is a private-provider tax credential-access waist. The rule is: **no tax right by private credential**. The public tax record, payment route, refund claim, notice response, and representative authority remain IRS public-law duties even when a private identity provider controls the account door.
