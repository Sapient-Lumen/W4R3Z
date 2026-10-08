# Start here — Moral Taxation rev0300

Rev0300 is the cross-border-reporting accountability pass. The priority change is concrete: international coordination, customs/CBAM border charges, remittance corridors, immigration/asylum/status fees, withholding/treaty/MAP relief, and GIR/claim-split routes now name concrete accountable actors, beneficiaries, bottlenecks, burden bearers, evidence packets, fallback dispute paths, and capacity duties.

## First route

1. Read `docs/10-framework/ideal-taxation-by-class-context-and-species.md` for the founding answer.
2. Use `docs/10-framework/decision-procedure.md` for routing.
3. For international coordination, customs/CBAM, tariffs, remittances, migration or status fees, treaty relief, withholding, MAP, double-tax protection, GIR exchange, or claim-split questions, start with `docs/00-meta/cross-border-reporting-accountability-refactor-rev0300.md`.
4. Before accepting any cross-border charge, report, fee, withholding, relief denial, exchange result, or claim split, check `docs/00-meta/actor-accountability-profiles.json` so the burden is not assigned to the foreign taxpayer, migrant, claimant, remitter, source state, host locality, or small administration merely because they are visible.
5. For health, food, utilities, nonprofit, municipal-bond, tribal, charity, or public-service/member-relief questions, use `docs/00-meta/social-floor-public-services-accountability-refactor-rev0299.md`.
6. For climate, environmental justice, water, fisheries, minerals, transport emissions, data-center local burdens, insurance backstops, offsets, or prefunding/security problems, use `docs/00-meta/environment-climate-commons-accountability-refactor-rev0298.md`.
7. For worker, household, care, child, education-debt, retirement, platform-benefit, data-minimization, or pension-pass-through questions, use `docs/00-meta/labor-care-benefits-accountability-refactor-rev0297.md`.
8. For coercive penalties and enforcement, use `docs/00-meta/legal-enforcement-accountability-refactor-rev0296.md`.
9. For public-finance waist questions, use `docs/00-meta/public-finance-core-accountability-refactor-rev0295.md`.
10. For AI/controller disputes, use `docs/00-meta/controller-ai-accountability-refactor-rev0294.md`.
11. For filing, refund, payment, preparer, service, contest, setoff, or timing problems, use `docs/00-meta/tax-admin-access-accountability-refactor-rev0293.md`.
12. Check `docs/00-meta/policy-action-profiles.json`, `docs/00-meta/remedy-profiles.json`, and `docs/00-meta/case-contracts.json` to keep action choice, remedy, and golden-case obligations executable.

## Machine surfaces

- `cube-index.json` — route records and axes.
- `docs/00-meta/actor-accountability-profiles.json` — responsibility-chain routing.
- `docs/00-meta/policy-action-profiles.json` — policy-action semantics and category-error guards.
- `docs/00-meta/remedy-profiles.json` — default moves, blocked moves, guardrails, and escalation triggers.
- `docs/00-meta/case-contracts.json` — executable golden-case obligations.
- `docs/00-meta/source-currentness-registry.json` — volatile source review dates.
- `MANIFEST.json` — exhaustive inventory with hashes.

## Release check

Run `make package`. It renders the scorecard, rebuilds the manifest, runs cube/source/remedy/case-contract/policy-action/actor-accountability audits, checks archive links and generated surfaces, then writes the revision zip in the parent directory.

Rev0300 narrows the current work to cross-border routes, where generic accountability can hide treaty-relief paywalls, withholding overcollection, hidden border pass-through, remittance corridor rents, status-access ransom, source-state erasure, and claim-split implementation failure.
