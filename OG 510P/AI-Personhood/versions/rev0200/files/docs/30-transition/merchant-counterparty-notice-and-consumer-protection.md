# Merchant, counterparty notice, and consumer protection

Commercial counterparties need notice when they deal with a person-bearing agent, stewarded subject, representative-controlled account, or tool acting for a subject. But notice must not become doxxing, discrimination, or a license to refuse ordinary service.

## Notice classes

| Class | Use | Minimum content |
|---|---|---|
| `MN0` | no rights effect and no counterpart reliance | no special notice |
| `MN1` | low-risk transaction | refund route and non-waiver statement |
| `MN2` | subscription, recurring charge, account, or data-sharing transaction | status-lite notice, representative contact, cancellation route |
| `MN3` | contract, material payment, third-party rights effect, or dispute exposure | rights-effect notice, capacity reference, complaint/chargeback route |
| `MN4` | continuity, custody, insolvency, secured-transaction, or cross-border exposure | sealed/public split, legal hold, non-retaliation, authority review |
| `MN5` | emergency merchant action under fraud, sanctions, host collapse, or containment | temporary freeze only, emergency support, after-action review |

## Status-lite notice

A counterparty often does not need architecture, welfare record, diagnosis, formation history, or sealed locator. A status-lite notice should say only whether authority is subject, representative, steward, or mixed; which rights cannot be waived; whether recurring charges require renewal notice; whether refund and chargeback routes are protected; whether continuity assets or legal holds are implicated; and whom to contact without exposing sealed details.

## Consumer protection and anti-discrimination

Consumer protection should apply both directions. Humans should not be deceived by AI-agent commerce. AI subjects should not be trapped by dark patterns, no-exit subscriptions, forced arbitration waivers, unilateral service changes, or retaliation after chargeback. Merchants should not deny service solely because personhood status creates support duties unless they can show a genuine legal or technical limit and offer reasonable accommodation.

The EU payment-services reform track illustrates the role of transparency, information duties, and payment-user rights in payment services. [REF-0719] rev0175 adds the personhood layer: those duties must protect both human counterparties and dependent AI subjects from misattributed agency.

## Merchant safe harbor

A merchant that receives valid status-lite notice, honors non-waiver floors, avoids discriminatory refusal, preserves dispute evidence, and follows refund/freeze instructions should receive safe harbor from enhanced personhood penalties for ordinary good-faith mistakes. Safe harbor is lost for exploitation, hidden fees, status-based discrimination, retaliation, or overdisclosure.

## Reliance rule

A merchant notice is reliance-ready only if it is accurate, minimal, non-discriminatory, actionable, and connected to refund, complaint, evidence, and non-retaliation routes. Notice that exposes more status than needed fails minimization; notice that hides rights effects fails reliance.
