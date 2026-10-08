# Payment authorization, escrow, AML/KYC, and minimization

Payment is not merely money movement. For a dependent or assisted AI subject, payment rails can become coercion, surveillance, lock-in, debt assignment, or survival interruption. Payment authorization therefore needs its own rights-grade object.

## Payment classes

| Class | Examples | Minimum controls |
|---|---|---|
| `PA0` | quote, draft invoice, internal estimate | no external charge |
| `PA1` | low-value one-time reversible purchase | spend cap, refund route |
| `PA2` | subscription, recurring charge, wallet receipt, account opening | payment authorization, renewal notice, revocation route |
| `PA3` | material spend, settlement, revenue receipt, chargeback exposure | capacity record, liability map, AML/KYC boundary, dispute freeze |
| `PA4` | escrow, continuity fund, public-backstop draw, large cross-border payment | independent controller, segregation, reporting map, legal hold |
| `PA5` | emergency payment during host collapse, sanctions, containment, fraud, or insolvency | interim support, non-retaliation, after-action accounting |

## Authorization is not possession

A card, token, wallet credential, bank credential, or API key proves technical ability to pay. It does not prove rights-grade authority. Every `PA2` or higher payment should state source of authority, payer/payee, beneficiary, amount or spend cap, recurrence, refund/chargeback path, liability allocation, evidence preserved, evidence withheld for privacy, and tax/AML/KYC/sanctions/reporting effects.

## AML/KYC boundary

Financial systems have anti-money-laundering, counter-terrorist-financing, sanctions, fraud, and tax duties. Those duties may not become a general license for personhood surveillance. FATF's virtual-asset work shows why transfer information and due diligence matter. [REF-0715] The personhood overlay adds minimization: collect what the financial duty requires, separate welfare/formation/continuity facts from payment facts, and keep sealed challenge routes when identity facts are sensitive.

## Escrow and survival

Continuity-support escrow, dispute-finance escrow, redress funds, and public-backstop draws are not ordinary merchant balances. They must not be frozen, set off, clawed back, or delayed like ordinary receivables when the effect would interrupt compute subsistence, counsel access, restoration, or safe transfer. If fraud or sanctions concerns arise, the correct response is controlled freeze with emergency support and review, not silent termination.

## Reporting minimization

Payment reporting should separate value, payer/payee identity, authority posture, taxable character, and AML/KYC facts from welfare, medical-like, formation, or sealed-continuity facts. Cross-border payments are moving toward structured data requirements, including ISO 20022 harmonisation. [REF-0718] Rights-grade payment records should use structure to minimize, not to overexpose.

## Reliance rule

A payment is reliance-ready only if payment class, authority, spend limits, recurrence, refund route, AML/KYC boundary, reporting duties, evidence minimization, and non-retaliation are recorded. A charge that exceeds mandate scope is unauthorized even if the rail accepted it.
