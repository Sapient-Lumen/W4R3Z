# 022 — Payee verification and the end of blind payments

**Status:** canon

## Thesis

As faster-payment regulation, fraud controls, and bank-side risk tooling move toward payee-name matching, account-directory lookups, sanctions-state screening, and pre-authorisation warning flows, the practical ability to send money will increasingly depend on passing a machine-mediated counterparty-validation layer rather than mainly on typing an account identifier and pressing send.

The scarce asset is no longer only a valid account number or enough funds.
It is increasingly the ability to supply counterparty data that a sending bank, receiving bank, directory, or payment-rail rulebook can validate quickly enough for payment initiation to remain low-friction.

## Why it matters

This changes where practical control sits in ordinary money movement.
The decisive moment is no longer only the after-the-fact fraud investigation, sanctions review, or customer-support dispute.
It is increasingly the earlier workflow in which the payment system asks whether the named recipient, the account identifier, and the sending context line up well enough for the payer to be allowed to proceed with confidence.

That matters because instant payments compress the time available for human correction.
If funds arrive in seconds, then fraud prevention, misdirection prevention, counterparty confirmation, and some sanctions screening logic have to move upstream into initiation.
The bottleneck is not merely whether a payment rail exists.
It is increasingly **preflight admissibility on money rails**.
That pulls account directories, match-tolerance rules, warning design, bank-to-bank query protocols, sanctions-state refresh cycles, enterprise payment software, and liability allocation deeper into the ordinary act of sending money.

This is related to `011`, `015`, `016`, and `020`, but it is not reducible to them.
`011` is about transaction rails that make economically meaningful events born-reportable.
`015` is about governed relays and trusted intermediaries.
`016` is about runtime standing.
`020` is about pre-start digital labour clearance.
This note is about a different shift: payment initiation itself increasingly moving from blind addressing toward **counterparty validation before authorisation**.

## Mechanism sketch

- EU law now makes the core move explicit. Regulation (EU) 2024/886 requires a payer’s payment service provider to offer a free verification-of-the-payee service, perform it immediately after the payer provides payee information, and do so before the payer is offered the possibility of authorising the credit transfer.
- The same regulation makes the shift broader than instant-payment speed alone. It requires matching of payee name and payment-account identifier for credit transfers, and it also requires payment service providers offering instant credit transfers to verify whether any of their users are subject to targeted financial restrictive measures immediately after new measures or amendments enter into force and at least once every calendar day.
- The European Payments Council has now operationalised the interbank layer. Its Verification Of Payee scheme provides inter-PSP rules, practices, and standards across SEPA, and the technical inter-PSP space is explicitly API-based and built on ISO 20022 resource elements.
- The UK’s Confirmation of Payee regime shows that this logic is not merely continental rulemaking. The Payment Systems Regulator directed the UK’s six largest banking groups to implement CoP, noted that those firms covered around 90% of Faster Payments and CHAPS transactions, and later pushed a phase-two move into a single technical environment so more banks could offer the service.
- Pay.UK’s operating description shows what this looks like in practice: Confirmation of Payee is an API-based peer-to-peer account-name-checking service used before initiating or collecting a payment, with a directory identifying participating organisations even though there is no central transaction-processing infrastructure.
- Enforcement now makes the layer feel real rather than decorative. In February 2026, the PSR fined Bank of Ireland UK more than £3.7 million for failing to comply with a Confirmation of Payee direction, demonstrating that preflight payee validation is becoming a supervised obligation rather than a nice-to-have fraud feature.
- The same direction of travel is now visible in the United States. Federal Reserve Financial Services markets a payee-name-verification service that lets financial institutions verify an intended payee’s name against routing and account-number data prior to issuing a payment, framing the tool as payment-rail-agnostic fraud and misdirection mitigation.
- Put together, these moves suggest a deeper pattern: some payment systems are shifting from **know the account string and accept the risk** toward **query the counterparty, surface the mismatch, refresh standing, then let the payer decide inside a governed warning flow**.

## What this speculation predicts

1. More payment systems will treat payee-name matching or equivalent counterparty-validation checks as a normal pre-authorisation step for ordinary digital transfers rather than as an optional anti-fraud overlay for exceptional channels.
2. Business payments software, treasury tools, and accounts-payable workflows will increasingly integrate payee-validation services so invoice settlement speed depends on counterparty-data cleanliness and directory reach, not merely on bank-account possession.
3. Disputes over payment fraud and misdirection will increasingly focus on match thresholds, warning wording, override logging, and directory coverage rather than only on customer negligence after the fact.
4. Freshly opened accounts, non-participating institutions, cross-border edge cases, and alias-heavy payment contexts will become more visible friction zones because they are harder to validate cleanly inside preflight flows.
5. Payment endpoints will increasingly need live discoverability, up-to-date participant metadata, and reliable status maintenance, making directories and validation operators more important than they appeared in the era of blind account addressing.

## Watchpoints

- more jurisdictions or major payment systems making payee-validation checks mandatory or strongly expected for ordinary account-to-account transfers
- enterprise payment software marketing built-in payee verification, counterparty validation, or warning-log retention as a core control rather than an add-on
- evidence that fraud and misdirected-payment liability regimes increasingly hinge on whether the payer saw, understood, or overrode a match warning
- expansion of counterparty-validation logic beyond classic domestic transfers into cross-border, request-to-pay, wallet, or alias-based payment contexts
- evidence that banks or regulators retreat from preflight validation because false positives, privacy limits, or directory-coverage gaps make the systems too unreliable to matter

## What would weaken this

- mandatory payee-verification regimes remaining geographically narrow, channel-specific, or easy to bypass so most money movement still behaves like blind account addressing
- institutions continuing to treat post-payment monitoring and reimbursement as sufficient, with little appetite for upstream counterparty validation at initiation time
- validation systems proving too inaccurate, too privacy-invasive, or too operationally brittle to become a durable condition of ordinary payment initiation
- instant-payment growth continuing without meaningful expansion of payee checks, sanctions-state refresh expectations, or directory-based counterparty validation

## Source anchors

- [SRC-119](../00-meta/bibliography.md#src-119)
- [SRC-120](../00-meta/bibliography.md#src-120)
- [SRC-121](../00-meta/bibliography.md#src-121)
- [SRC-122](../00-meta/bibliography.md#src-122)
- [SRC-123](../00-meta/bibliography.md#src-123)
- [SRC-124](../00-meta/bibliography.md#src-124)
