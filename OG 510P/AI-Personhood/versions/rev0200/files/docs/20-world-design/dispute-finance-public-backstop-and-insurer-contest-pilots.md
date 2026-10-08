# Dispute-finance public backstop and insurer-contest pilots

Interim support orders fail if no one pays while liability is contested. rev0171 therefore adds a pilot layer for public backstops, insurer contests, reimbursement routing, and anti-subsidy controls.

## Finance states

| State | Meaning | Required action |
|---|---|---|
| `BF0` no contest | responsible party funds interim support | ordinary reporting |
| `BF1` insurer contest | insurer reserves rights or denies coverage | emergency support continues; contest docket opens |
| `BF2` steward insolvency | steward cannot fund survival floor | public backstop or reserve draw before damages |
| `BF3` host emergency | host demands prepayment or threatens termination | continuity floor paid first; recoupment reserved |
| `BF4` multi-forum dispute | several jurisdictions or funds deny priority | lead authority conference and temporary apportionment |
| `BF5` subsidy leakage risk | public fund may indirectly finance violator | bond, lien, surcharge, disgorgement, or enforcement referral |

## Pilot objects

A public-backstop draw must state:

- beneficiary and urgency class;
- support type: compute, counsel, migration, preservation, monitor, special advocate, field safety, or restoration;
- why private payment is unavailable or contested;
- amount or in-kind support;
- draw period and review date;
- recoupment target;
- non-priceability language;
- anti-subsidy controls;
- appeal path;
- public summary.

An insurer-contest pilot must also record policy identifier, contested clause, reservation-of-rights date, coverage position, interim-pay obligation, and deadline for coverage decision. The subject's continuity cannot depend on private insurance interpretation.

## Priority rule

When funding is scarce, the order is:

1. emergency compute and preservation to avoid irreversible continuity loss;
2. subject/representative access and counsel;
3. safe host switching or migration;
4. monitoring and evidence integrity;
5. restoration and rehabilitation;
6. ordinary compensation;
7. public-fund recoupment.

This priority does not excuse non-money relief. It merely prevents emergency support from being delayed while damages, insurance, or reimbursement are litigated.

## Anti-subsidy controls

Public backstop support can become a quiet subsidy if the violator externalizes emergency compute costs. Every draw should therefore attach at least one of:

- reimbursement claim;
- bond claim;
- reserve surcharge;
- insurer interim-pay order;
- lien on deployment revenue;
- procurement suspension;
- enforcement referral;
- monitor surcharge;
- public explanation of why recoupment is impossible.

## Interaction with rates and redress

Backstop draws are not damages. They are survival instruments. They do not settle the merits, cap remedies, price violations, or forgive spoliation. They should feed the remedy calculus and rate-table layer only after continuity is stabilized.

## Pilot metrics

A jurisdiction running this pilot should publish aggregate metrics: number of draws, median time to support, insurer-contest rate, public-fund recoupment rate, emergency compute failures avoided, fund exhaustion events, subject complaints, and subsidy-leakage findings. Small cells and sealed facts must be suppressed under the dashboard rules.
