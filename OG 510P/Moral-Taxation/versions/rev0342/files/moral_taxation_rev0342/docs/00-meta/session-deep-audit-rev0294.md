# Session deep audit — rev0294

Rev0294 follows rev0293's working discipline: choose a concrete high-risk slice and make it more executable rather than adding another abstract registry layer.

## Corrected in rev0294

- All 21 `controller_ai` actor-accountability profiles now name concrete beneficiaries or rent recipients rather than `beneficiary_or_rent_recipient_to_trace`.
- All 21 now use route-specific evidence packets rather than the inherited generic `benefit_or_rent_trace` bundle.
- The family now distinguishes AI-law role evidence, future personhood/status claims, automation surplus, controller boundary ranking, controller-map packet governance, model-assisted administration/enforcement, public-input reciprocity, and taxpayer-side AI/preparer accountability.
- The actor-accountability audit now rejects controller-AI placeholder regression and requires controller-map/model-assisted profiles to include route-specific evidence.
- Key controller-AI calibration memos now include explicit accountability maps.

## Why this was the priority

The controller-AI family is where the cube is most exposed to both evasion and overreach. If responsibility is assigned to “the model,” nobody can repair. If it is assigned to the most visible app, host, remitter, or registry contact, the wrong party may be taxed or punished. If it is assigned to the taxpayer scored by a model, public administration becomes black-box burden shifting. If it is assigned to every participant, the archive loses the difference between governance, infrastructure, remittance, audit, and ordinary use.

The refactor therefore makes the profile layer answer who controls the deployment, who benefits from opacity or surplus, who holds the channel, who bears the floor risk, and what evidence decides the route.

## Residual risk

The archive still has 95 beneficiary placeholders and 117 generic evidence bundles outside the two completed families. That is materially better than rev0293 but still too high. The remaining problem is not schema coverage; it is substantive specificity.

The next highest-value pass should likely focus on a bounded `public_finance_core` cluster, because that family is large enough to hide many tax/fee/mandate/action mistakes and currently contains the most remaining generic accountability language.

## Operating lesson

Do not let “profile exists” mean “responsibility is assigned.” The existence of a JSON record, route record, or source currentness entry can become ceremony unless the route names the beneficiary, bottleneck, burden bearer, non-responsible conduit, and public fallback duty in words that would survive a live dispute.
