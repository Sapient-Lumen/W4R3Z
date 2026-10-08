# Model-input execution and assumption-boundary refactor — rev0329

Active revision: rev0329. Codename: `model-input-execution-assumption-boundary-refactor`. Generated: 2026-06-18T16:18:00Z.

## What changed

rev0328 made producer execution reusable, but local model evidence could still be generated from adapter packet shape. rev0329 adds an explicit model-input bundle boundary. Quantitative, floor-delivery, and no-go producer outputs now require input values, units, assumptions, uncertainty parameters, locators, and stable input hashes before they can satisfy adapter execution.

## Model-input bundle audit

Model-input runtime status: explicit_model_input_bundle_generated
Answer packets checked: 122
Model adapter checks: 859
Model input records: 859/859
Complete model input records: 859/859
No-input local-model evidence produced: 0/0
Explicit-input local-model evidence produced: 859/859
Explicit-input model adapters satisfied: 807/807
Explicit-input no-go adapters blocked: 52/52
Legacy shape-only model evidence blocked: 859/859

## Evidence-producer execution audit

Evidence-producer runner runtime status: evidence_producer_runner_invoked
Answer packets checked: 122
Adapter checks: 1724
Explicit model input records: 859/859
Interface-fixture evidence produced: 1724/1724
Interface-fixture satisfied adapters: 1724/1724
No-input local-model evidence produced: 0/0
No-input local-model skipped adapters: 1724/1724
Local-model evidence produced: 859/859
Local-model external adapters skipped: 865/865
Local-model satisfied adapters: 807/807
Local-model missing external adapters: 865/865
Local-model no-go blocks: 52/52
Legacy shape-only model evidence blocked: 859/859
Local-model can-finalize answers: 0/122
Stale-evidence blocked adapters: 1724/1724
Jurisdiction uncertain-scope block count: 1

## Substantive effect

The runtime chain is now:

`facts -> candidate routes -> selected profiles -> claim packets -> precedence order -> final disposition -> decision adapters -> adapter execution evidence validation -> registered evidence-producer request gates -> evidence-producer runner -> explicit model-input bundle gate`

The anti-waste correction is that local reference models no longer create outputs merely because an adapter id exists. The runner with no input bundle produces zero model evidence. A complete input bundle produces model evidence with hashes and assumptions, but finalization still blocks when current law, jurisdiction scope, external no-go review, or stale-evidence checks are unresolved.

## Remaining frontier

Replace the reference input fixture with real jurisdictional microdata, delivery-capacity inputs, incidence assumptions, and expert no-go review records. The archive should continue to validate evidence bundles without storing those perishable model inputs or outputs as doctrine.
