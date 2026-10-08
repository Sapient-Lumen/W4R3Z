# Payment-redress tests matrix

Generated for `rev0799` from `metadata/payment_redress_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `calculation_and_route_explanation` calculation and route explanation | Can the claimant and public audit record see how the amount was calculated and what route choices were available? | `857`, `874`, `897` | Treat the amount as provisional until calculation, route alternatives, and pressure context are visible. |
| `claimant_owner_and_authority` claimant owner and authority | Is the person, business, estate, family member, representative, or support-scheme recipient correctly identified, and is the public payment owner named? | `817`, `857`, `884`, `894`, `897` | Do not count a claim as clean while claimant identity, representative authority, or public owner is unresolved. |
| `dispute_review_and_extension_clock` dispute, review, and extension clock | Can the claimant challenge, extend, reopen, go to court, or preserve rights before delay, disallowance, deadline, or scheme closure defeats the claim? | `817`, `857`, `861`, `884`, `897` | Do not score closure or disallowance as final when review, extension, or limitation-period protection is absent or unclear. |
| `evidence_burden_and_lost_records` evidence burden and lost records | Does the scheme handle missing, state-controlled, institution-controlled, historic, or corrupted records without unfairly defeating the claimant? | `857`, `861`, `897` | Shift or soften the burden where the institution caused evidentiary uncertainty, and publish how uncertain claims are handled. |
| `fraud_control_and_integrity_boundary` fraud control and integrity boundary | Are fraud, promoter, duplicate, identity, or improper-payment screens documented without creating indefinite limbo for valid claims? | `857`, `874`, `897` | Fraud control is not legitimate as an unbounded hold; require time-bounded status and rights preservation. |
| `interim_final_and_fixed_sum_boundary` interim, final, and fixed-sum boundary | Does the record distinguish partial, interim, fixed-sum, top-up, adjusted, periodic, lump-sum, full-assessment, and final payments? | `857`, `884`, `897` | Do not count partial or fast-route payment as full repair without finality, alternatives, and reopening / challenge rules. |
| `legal_or_harm_basis` legal or harm basis | Does the record state the statute, regulation, settlement, scheme rule, tax period, conviction status, support registration, or compensable harm that makes money payable? | `814`, `857`, `874`, `894`, `897` | Do not pay, deny, or close without a traceable basis for why the claim is payable or not payable. |
| `payment_state_ladder` payment-state ladder | Are registered, invited, started, complete, offered, accepted, issued, received, final, challenged, reopened, rejected, and expired states separated? | `857`, `861`, `884`, `894`, `897` | Do not use aggregate totals as proof of repair unless payment states are separately published. |
| `publication_cost_and_learning_loop` publication, cost, and learning loop | Does public reporting separate claimant redress from administration/legal costs and show corrections, lessons, remaining inventory, and future programme changes? | `857`, `861`, `884`, `897` | Do not treat public reporting as adequate if totals hide costs, corrections, pending inventory, or lessons for future schemes. |
| `support_family_and_vulnerability_tail` support, family, and vulnerability tail | Are support payments, bereaved partners, estates, affected family members, illness, age, disability, trauma, and hardship treated as payment design fields rather than afterthoughts? | `817`, `879`, `884`, `894`, `897` | Do not call the main claimant route complete if derivative, support, estate, or vulnerable claimant tails are unresolved. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `898` | `calculation_and_route_explanation`, `claimant_owner_and_authority`, `dispute_review_and_extension_clock`, `evidence_burden_and_lost_records`, `interim_final_and_fixed_sum_boundary`, `legal_or_harm_basis`, `payment_state_ladder`, `publication_cost_and_learning_loop`, `support_family_and_vulnerability_tail` |
| `899` | `calculation_and_route_explanation`, `claimant_owner_and_authority`, `dispute_review_and_extension_clock`, `evidence_burden_and_lost_records`, `interim_final_and_fixed_sum_boundary`, `legal_or_harm_basis`, `payment_state_ladder`, `support_family_and_vulnerability_tail` |
| `900` | `calculation_and_route_explanation`, `claimant_owner_and_authority`, `dispute_review_and_extension_clock`, `fraud_control_and_integrity_boundary`, `legal_or_harm_basis`, `payment_state_ladder`, `publication_cost_and_learning_loop` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `814` | 1 |
| `817` | 3 |
| `857` | 9 |
| `861` | 4 |
| `874` | 3 |
| `879` | 1 |
| `884` | 6 |
| `894` | 4 |
| `897` | 10 |

## Use rule

Run payment-redress tests whenever a public body owes or may owe money through compensation, redress, tax refund, refundable credit, support-scheme conversion, settlement implementation, wrongful-conviction payment, emergency relief, or administrative-harm repair. Separate claim registration, offer, acceptance, payment issuance, payment receipt, interim, final, challenge, reopening, fraud-screen, and remaining tails before scoring repair or closure.
