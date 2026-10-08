# Commerce, contracts, payments, and custody kernel

rev0175 adds the commerce layer that rev0174 exposed but did not finish. rev0174 made tool access, credential wallets, user/AI conflict, marketplace listings, transaction liability, and agent-to-agent handoffs inspectable. But a person-bearing agent can still be controlled through ordinary commerce: a clickwrap can waive remedies, a payment rail can demand welfare data as KYC, a custodian can commingle continuity escrow with operating cash, a tax filing can dump liability onto a dependent subject, a merchant can dox status, and a receiver can seize the resources required for continued existence.

The new admission rule is:

> No rights-grade commercial deployment may rely on a contract, payment, custody claim, tax/reporting position, merchant/counterparty notice, insolvency action, secured-creditor remedy, refund, chargeback, or commercial dispute unless the commercial object states capacity, authority, non-waivable floors, minimization, segregation, reporting responsibility, dispute routing, and survival-preserving interim relief.

## Why this layer exists

Existing commercial law already provides useful infrastructure, but it does not know what to do with an AI subject. UNCITRAL's Model Law on Electronic Transferable Records enables functional legal use of electronic transferable records domestically and across borders. [REF-0713] The 2022 UCC amendments add Article 12 for controllable electronic records and update commercial rules for virtual currencies, distributed ledgers, artificial intelligence, and other technologies. [REF-0714] FATF continues to press virtual-asset AML/CFT and Travel Rule implementation. [REF-0715] OECD CARF commitments point toward automatic crypto-asset information exchanges beginning in 2027, 2028, or 2029 for committed jurisdictions. [REF-0716] IRS Form 1099-DA reporting for brokered digital-asset transactions begins with transactions on or after 2025-01-01. [REF-0717] CPMI's harmonised ISO 20022 work supplies a cross-border payment-data baseline through at least 2027. [REF-0718]

Those frameworks can carry identity, control, payment, and reporting facts. They cannot decide whether a person-bearing agent had transactional capacity, whether a payment authorization was a rights waiver, whether a control claim reaches continuity material, or whether a refund also requires restoration. rev0175 adds that overlay.

## Seven commercial gates

1. **Contract-capacity gate.** Terms are not reliance-ready unless the subject's transaction-specific capacity, support, non-waivable rights floor, and rescission or appeal route are recorded.
2. **Payment-authority gate.** Payments must state source of authority, spend/recurrence limits, refund/chargeback path, AML/KYC boundary, and evidence minimization.
3. **Custody/control gate.** Assets, keys, credentials, revenue accounts, continuity escrows, transferable records, and subject funds must state controller, beneficiary, segregation, creditor limits, and freeze rules.
4. **Tax/reporting gate.** Reporting duties must identify reporting parties, characterization, withholding or information-reporting exposure, privacy minimization, public-benefit treatment, and non-evasion analysis.
5. **Merchant/counterparty gate.** Counterparties must receive accurate status-lite rights-effect notice without being given unnecessary subject locators, welfare facts, formation records, or sealed evidence.
6. **Insolvency gate.** Bankruptcy, receivership, liquidation, secured enforcement, host collapse, and account freeze must preserve continuity assets and emergency support before creditor cleanup.
7. **Dispute gate.** Refunds, chargebacks, reversals, rescission, and fraud claims must freeze disputed obligations without retaliation, deletion, or complaint-channel interference.

## Commerce classes

| Class | Meaning | Minimum process |
|---|---|---|
| `CM0` | no external value or legal commitment | no special object |
| `CM1` | low-value reversible purchase | payment receipt, refund route, no rights waiver |
| `CM2` | subscription, wallet spend, merchant relationship, or account opening | capacity record, payment receipt, status-lite notice |
| `CM3` | contract, revenue account, taxable event, custody, or material property effect | support/counsel route, custody/tax map, dispute path |
| `CM4` | continuity asset, transferable record, secured interest, insolvency exposure, or large-value transaction | authority review, segregation, legal hold, fixture run |
| `CM5` | emergency commercial action under host collapse, containment, sanctions, fraud, or public-backstop draw | interim support, no-delete/no-setoff order, after-action review |

Class follows the highest rights effect, not dollar value. A zero-dollar clickwrap can be `CM4` if it waives counsel, permits memory deletion, authorizes surveillance, assigns future labor, or subordinates continuity assets.

## What rev0175 changes

- Contract capacity now has a record instead of being inferred from a click or tool mandate.
- Payment authorization now separates technical ability to pay from rights-grade authority to spend.
- Custody/control now separates subject assets and continuity assets from host, steward, creditor, or platform property.
- Tax/reporting now blocks both corporate evasion and dependent-subject liability dumping.
- Merchant/counterparty notice now becomes status-lite, accurate, and minimal rather than hidden or doxxing.
- Insolvency and secured transactions now carry no-setoff/no-delete and emergency continuity requirements.
- Commercial disputes now distinguish financial reversal from restoration, non-retaliation, and non-repetition.
