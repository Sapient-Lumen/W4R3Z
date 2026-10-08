# Exposure State Vocabulary

This vocabulary supports `31-exposure-liability-lifecycle.md` and prevents risk-transfer dossiers from multiplying around the same few concepts.

## Allocation and attachment

- `unallocated-exposure` — no actor, policy, warranty, reserve, public fund, or residual claimant is clearly responsible for the loss class.
- `allocated-by-contract` — a contract assigns responsibility, even if practical recovery remains uncertain.
- `coverage-attached` — a policy, bond, warranty, guarantee, escrow, or fund appears capable of responding to the exposure.
- `certificate-evidence-accepted` — a certificate or proof of protection has been accepted as sufficient for a workflow, without necessarily proving actual coverage.
- `endorsement-required` — the base proof is insufficient unless an endorsement, rider, additional-insured status, waiver, or special condition is added.
- `nonresponsive-protection` — a visible protection artifact exists, but does not respond to the relevant loss class.

## Conditions and triggers

- `condition-precedent-pending` — coverage or warranty response depends on a still-unmet condition.
- `warranty-breached` — a representation, maintenance promise, security control, update obligation, or proof-quality warranty has failed.
- `notice-clock-running` — a duty to notify has started but the notice has not yet been completed or accepted.
- `materiality-determination-pending` — the incident may be material, reportable, or financially significant, but the decision state is not yet final.
- `trigger-disputed` — parties disagree about whether an event falls within the trigger grammar.

## Coverage, defense, and exclusions

- `coverage-position-reserved` — the responding party has not accepted full coverage / warranty responsibility and is preserving defenses.
- `defense-under-reservation` — defense or response costs are being funded while rights are reserved.
- `exclusion-flagged` — an exclusion or non-covered class is plausible enough to govern workflow routing.
- `exclusion-final` — the protection is determined not to respond to the loss class.
- `control-rights-disputed` — parties disagree over who controls remediation, defense, settlement, disclosure, ransom, recall, or repair.

## Retentions, limits, and reserves

- `deductible-unmet` — the insured or protected party has not yet crossed the deductible threshold.
- `sir-open` — a self-insured retention is absorbing first-layer loss and shaping response behavior.
- `limit-eroding` — costs are reducing the remaining available protection.
- `aggregate-approaching` — accumulated losses are nearing an aggregate cap.
- `reserve-held` — capital, accounting reserve, escrow, bond, or holdback remains locked against a tail.
- `reserve-release-pending` — release depends on additional evidence, elapsed time, remedy closure, or regulator/counterparty sign-off.

## Recovery, renewal, and closure

- `indemnity-chain-mapped` — pass-through responsibility has been traced across suppliers, delegates, maintainers, platforms, brokers, and customers.
- `subrogation-preserved` — evidence, notice, and waiver controls preserve recovery rights after payment.
- `subrogation-impaired` — recovery rights have been weakened by late notice, destroyed evidence, settlement, waiver, or missing attribution.
- `loss-run-sensitive` — the event may affect future underwriting, pricing, deductibles, retentions, limits, exclusions, or eligibility.
- `renewal-restricted` — renewal is conditioned on remediation, controls, exclusions, higher retentions, or lower limits.
- `tail-open` — the exposure remains live after the transaction, incident, correction, sale, closure, or release.
- `claim-closed` — the claim or exposure has a closed state, with archive and reopening rules.

## Usage rule

Do not create a new state label unless it changes at least one of: notice, defense, payment, reserve, exclusion, limit, recovery, renewal, or reliance. Otherwise, use an existing term and record the sector-specific nuance in the dossier body.
