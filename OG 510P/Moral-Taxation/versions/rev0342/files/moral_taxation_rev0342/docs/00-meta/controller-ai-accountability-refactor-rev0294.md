# Controller-AI accountability refactor — rev0294

Rev0294 converts the `controller_ai` actor-accountability family from valid placeholders into route-specific accountability maps. The goal is practical: before the archive assigns a tax, fee, refund freeze, public-input contribution, controller-map obligation, AI-preparer remedy, or model-assisted enforcement safeguard, it should identify who actually controls the system, who benefits, who holds the bottleneck, who bears the burden, and which public fallback duty survives.

## Why this was the next risky slice

The `controller_ai` family sits on a classification seam where errors can become large and hard to unwind. If the archive lets a profile say only “AI controller, deployer, or accountable public user,” four failures follow:

1. **model-as-actor evasion** — the system is treated as the responsible actor even though a person, firm, agency, vendor, signer, or controller group controls deployment and repair;
2. **visible-interface capture** — the invoice, brand, registry contact, host, app store, or remitter is treated as controller without evidence of governance;
3. **black-box public administration** — a model score or generic notice hardens into refund delay, audit escalation, adjustment, or enforcement without a reviewable packet;
4. **taxpayer-side liability mirroring** — preparer/vendor/agent opacity creates the error, but penalties, delay, and refund loss are shifted to the taxpayer.

Those are not merely doctrinal problems. They decide who keeps logs, signs maps, updates stale facts, accepts counter-maps, preserves review, funds transition, controls refund destinations, and repairs public-channel failures.

## Concrete changes

The pass rewrites all 21 `controller_ai` profiles in `actor-accountability-profiles.json`.

| Metric | Before rev0294 | After rev0294 |
|---|---:|---:|
| `controller_ai` profiles | 21 | 21 |
| controller-AI beneficiary placeholders | 21 | 0 |
| controller-AI generic `benefit_or_rent_trace` evidence bundles | 21 | 0 |
| archive-wide beneficiary placeholders | 116 | 95 |
| archive-wide generic evidence bundles | 138 | 117 |
| primary-accountable actor categories | 30 | 50 |

The new profile set separates six clusters:

1. **role crosswalk and personhood/status claims** — AI-law roles and future status claims are evidence channels, not automatic tax subjecthood or liability shifts.
2. **automation surplus and public-input reciprocity** — automation dividends and public-input claims attach to controllers or beneficiaries that capture residual upside, not to ordinary users, workers, creators, or the tool itself.
3. **controller boundary ranking** — primary responsibility follows durable governance, continuation power, and residual upside; co-controller treatment is layer-specific.
4. **controller-map packet governance** — map content, signer authority, versioning, reuse, redaction, event logs, confidence, contest, and verification each now has an accountable record holder or reviewer.
5. **model-assisted public administration** — agency model owners and decision officials owe model/version, data-category, notice, review, red-team, rollback, and human-gate records.
6. **taxpayer-side AI/preparer reliance** — paid preparers, software vendors, filing agents, wallets, and refund rails carry accountability when they control source traceability, signatures, submission, or refund destination.

## Profile design rule

A controller-AI profile now has to answer five questions in a route-specific way:

1. Who has **governance or decision power** for this route?
2. Who receives the **upside or rent** from opacity, automation, safe-harbor status, public inputs, or burden shifting?
3. Which actor controls the **bottleneck or channel**: model pipeline, controller-map registry, attestation lane, refund wallet, filing agent, or review queue?
4. Who is the **burden bearer** if the assignment is wrong?
5. What **evidence packet** can prove or rebut the assignment without turning the route into a universal data-room?

## New release gate

`tools/audit_actor_accountability_profiles.py` now makes controller-AI placeholder regression fatal. A `controller_ai` profile may not keep `beneficiary_or_rent_recipient_to_trace`, may not use generic `benefit_or_rent_trace` evidence, must carry multiple responsibility bases, and controller-map or model-assisted routes must include route-specific evidence for maps, models, review, and notice.

## Substantive document updates

Five route documents now have explicit accountability-map sections:

- `ai-regulatory-role-controller-evidence-crosswalk-ladder.md`
- `controller-boundary-and-co-controller-ranking-ladder.md`
- `controller-map-minimum-contents-attestation-and-update-cadence-standard.md`
- `model-assisted-tax-administration-minimum-standard.md`
- `model-assisted-enforcement-red-team-standard.md`
- `taxpayer-side-ai-preparer-agent-reliance-and-liability-ladder.md`

The common theme is narrowness. The archive should not tax “AI,” punish the scored taxpayer for hidden model governance, or treat every interface as a controller. It should assign responsibility to the actor with control, benefit, bottleneck authority, evidence access, or public fallback duty.

## Remaining specificity debt

After rev0294, the largest remaining actor-accountability specificity debt is outside `tax_administration_access` and `controller_ai`. The highest-volume remaining placeholder family is `public_finance_core`, followed by labor/care/benefits, legal-enforcement-penalty, and environment/climate/commons. The next pass should probably take a bounded public-finance cluster rather than creating a general archetype registry first.
