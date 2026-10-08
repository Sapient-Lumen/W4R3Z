# Session deep audit — rev0293

This memo records the current working diagnosis after the tax-administration-access accountability refactor. The pass intentionally favors route-specific substance over another layer of taxonomy.

## Corrected in rev0293

- All 17 `tax_administration_access` actor-accountability profiles now name concrete beneficiaries/rent recipients rather than `beneficiary_or_rent_recipient_to_trace`.
- All 17 now use route-specific evidence packets rather than the inherited generic `benefit_or_rent_trace` bundle.
- Public filing/refund and mandatory private tax rail ladders now include explicit accountability maps.
- `necessary-private-rail-and-channel-incidence-routing.md` now requires the access-rent beneficiary to be named at handoff.
- `tools/audit_actor_accountability_profiles.py` now makes tax-administration placeholder regression release-fatal.
- `make package` now creates a zip through `tools/package_release.py` after the release gate passes.

## Why this was the priority

The riskiest practical failures in the cube are not abstract classification errors. They are ordinary access failures: refund freezes, bankless exclusion, preparer or software dependency, identity dashboard lock-in, service deserts, uncorrected third-party records, setoff without usable notice, and cashflow timing rules that move public friction onto protected taxpayers.

Those failures all require a real accountability answer. Naming “the public channel owner” is not enough when a software partner, preparer, bank, wallet, processor, identity vendor, court collector, reporter, setoff recipient, escrow holder, or agency fund receives the upside or controls the repair channel.

## Residual risk

The rest of the actor-accountability layer remains structurally valid but still too generic in many families. After this pass, 116 profiles outside tax administration still use the generic beneficiary placeholder, and 138 profiles still use the generic evidence bundle. The next highest-value pass should convert another route family in the same way rather than building a universal archetype registry first.

## Recommended next work

1. Repeat this route-family specificity pass for `controller_ai` or the largest `public_finance_core` clusters.
2. Add a non-blocking axis-hygiene report that counts singleton axis values and suggests which ones should become route-local tags.
3. Add a source-currentness due queue, but keep it operational and short; do not let it become a parallel doctrine system.
4. Keep using `make package` so packaging drift is caught by the same release workflow as the manifest and profile audits.
