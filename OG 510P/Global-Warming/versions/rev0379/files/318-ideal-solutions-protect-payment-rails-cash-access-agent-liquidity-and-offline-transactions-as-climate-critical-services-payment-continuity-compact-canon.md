---
id: '318'
revision_added: rev0271
status: canon
object_type: service_continuity
domain_tags:
- payments
- cash
- banking
- mobile_money
- benefits
- remittances
- financial_inclusion
service_floor:
- payment_rail_continuity
- cash_access
- agent_liquidity
- emergency_transaction_continuity
hazard_tags:
- outage
- telecom_failure
- cyber
- flood
- heat
- conflict
- displacement
- bank_failure
- liquidity_shock
clock_tags:
- emergency_clock
- finance_clock
- recovery_clock
- learning_clock
actor_tags:
- central_bank
- payment_system_operator
- bank
- mobile_money_provider
- agent_network
- benefit_agency
- merchant
- regulator
instrument_tags:
- cash
- offline_mode
- liquidity_support
- fee_cap
- standstill
- prioritize
- disclose
- redress
routes_to:
- '20'
- '289'
- '290'
- '291'
- '292'
- '293'
- '294'
- '317'
- '442'
source_ids:
- S444
- S567
- S568
- S569
upstream_dependencies:
- power
- telecoms
- cash_supply
- liquidity
- identity_records
- merchant_network
- settlement_system
- agents
- public_notice
downstream_consequences:
- food_inaccessibility
- rent_arrears
- medicine_gap
- evacuation_failure
- debt_spiral
- remittance_failure
- benefit_exclusion
- social_unrest
equity_lenses:
- unbanked_people
- women_without_account_control
- migrants
- informal_workers
- elderly_people
- disabled_people
- rural_households
- people_without_smartphones
degraded_modes:
- cash_distribution
- paper_voucher
- hybrid_offline_payment
- emergency_fee_cap
- temporary_kyc_flexibility
- agent_float_support
- debt_standstill
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- telecom_dependency
- power_dependency
- agent_liquidity
- settlement_delay
- id_requirement
- fraud_controls
- cash_distribution
- merchant_acceptance
failure_modes:
- digital_payment_collapse
- no_cash_out
- agent_empty_float
- benefit_unspendable
- remittance_block
- offline_claim_overpromise
- fraud_lockout
proof_ledgers:
- payment_uptime_log
- cash_out_map
- agent_liquidity_log
- offline_transaction_log
- fee_fraud_complaint_log
- benefit_spendability_test
restoration_conflicts:
- cash_for_households_vs_businesses
- offline_limits_vs_inclusion
- fraud_control_vs_access
- bank_branch_security_vs_continuity
assurance_tests:
- seven_day_payment_outage_drill
- agent_liquidity_stress_test
- paper_voucher_redemption_test
- emergency_benefit_spendability_test
---
# 318 — Ideal Solutions: Protect payment rails, cash access, agent liquidity, and offline transactions as climate-critical services

## Claim

Files `289` and `290` treat household finance as a climate service.
This file adds the rail beneath the household: **payment systems, cash access, agent liquidity, merchant acceptance, remittances, benefit spendability, and offline transaction modes are climate-critical services, not fintech conveniences.**

A disaster payment is useless if the recipient cannot cash out, the merchant cannot accept it, the phone is dead, the tower is offline, the agent has no liquidity, the identity check fails, the fee is predatory, or the bank branch is closed.
A digital benefit is not resilient merely because it was sent.
It must be spendable under the conditions that created the need.

World Bank Findex data already shows the gap between account access and emergency resilience: many people have accounts, but far fewer can reliably access extra money in an emergency [S444].
BIS and Federal Reserve offline-payment work sharpens the technical reality: offline payment capability can support resilience and inclusion, but many systems are hybrid, few are fully offline at scale, and security, privacy, double-spending, clearing, settlement, and liability risks remain real [S567][S568].

## Fast rule

**Any climate packet that promises cash, vouchers, benefits, insurance, remittances, rent support, medicine access, evacuation support, repair grants, or emergency procurement must prove that money can be received, held, spent, cashed out, transferred, documented, and contested during outage.**

## Minimum service floor

The floor includes:

1. cash availability and safe cash-out points;
2. agent and ATM liquidity;
3. digital-payment uptime and degraded-mode acceptance;
4. emergency benefit delivery and spendability;
5. remittance continuity;
6. merchant acceptance for food, medicine, transport, shelter, fuel / charging, and repair;
7. temporary KYC and documentation flexibility with fraud controls;
8. fee caps, scam monitoring, and rapid redress;
9. debt standstills, utility shutoff protection, and claims deadlines where needed;
10. accessible, language-appropriate, non-smartphone access.

House rule: **a transfer is not relief until it buys something necessary.**

## Offline realism

The archive should not pretend that “offline payments” are magic.
The Federal Reserve review finds that many offline-branded payment systems are hybrid: they allow some transactions when a device or merchant is temporarily offline, but clearing and settlement still need connectivity later [S568].
BIS Project Polaris similarly treats offline payments as a design domain involving resilience, inclusion, privacy, device security, limits, and risk management [S567].

Therefore the climate rule is:

- keep cash alive as a public fallback where digital rails fail;
- support hybrid offline options where they are honest about limits;
- pre-set transaction caps, loss allocation, and dispute rules;
- avoid forcing vulnerable people into tools they cannot use;
- test payments at the point of use, not only at the sender ledger.

House rule: **do not replace cash with an untested promise of offline digital rescue.**

## Agent-liquidity rule

Mobile money, banking correspondents, post offices, retailers, and payment agents are part of the service floor.
They need:

- float and cash support;
- restoration priority for power and telecoms;
- fraud and robbery protection;
- emergency fee limits;
- clear public maps;
- backup identity and recipient verification;
- transport access for replenishment;
- grievance channels.

A payment system can be technically online while neighborhood liquidity is empty.

## Minimum proof ledger

| Question | Evidence required |
|---|---|
| Could people receive money? | successful payment, rejection, queue, and error logs |
| Could people spend it? | merchant acceptance and essential-goods spendability tests |
| Could people cash out? | agent liquidity, ATM status, branch status, and cash-delivery logs |
| What happened offline? | hybrid/offline transaction record, settlement delay, and loss allocation |
| Who was excluded? | no-ID, no-phone, disability, gender-control, migrant, rural, and custody access logs |
| What abuse occurred? | fee, scam, coercion, fraud, and complaint records |
| What changed after failure? | funded liquidity, rule change, new fallback, or provider sanction |

## What this routes to

- use `318` when a prompt asks about emergency cash, offline payments, CBDC, mobile money, remittances, benefit delivery, cash-out, agent networks, disaster finance, insurance payouts, or why digital relief fails;
- pair with `289` and `290` for household finance;
- pair with `317` for telecom and digital dependencies;
- pair with `291` and `292` for identity, legal deadlines, debt, and appeals;
- pair with `275`, `316`, and `319` when payments decide whether food, medicine, or relief can be accessed.

## Compression rule

**Climate money is a service floor only when cash, agents, merchants, digital rails, offline modes, identity flexibility, fee control, and redress work under outage.**

## Fragile-context rule

Payment resilience is not just a software property. In fragile or conflict-affected settings, the payment floor also depends on trusted agents, liquidity movement, cyber and fraud controls, dispute channels, interoperability, proportional identity rules, and a regulator that can keep essential transactions moving without pretending every user has stable power, connectivity, documents, or device control. [S569]

---
Citations point to `sources/register.md`.
