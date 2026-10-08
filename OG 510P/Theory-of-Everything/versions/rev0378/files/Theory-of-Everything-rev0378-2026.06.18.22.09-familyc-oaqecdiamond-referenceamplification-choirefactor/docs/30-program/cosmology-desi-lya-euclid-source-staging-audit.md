# rev0332 cosmology DESI/Lyman-alpha/Euclid source-staging audit

## Risk targeted

The late-time cosmology lane can overcredit public DESI DR2 chains, follow-up interpretation papers, and future Euclid runway as if they were one acquired dark-energy witness. That is unsafe because the public chain/posterior product, underlying spectra/redshift release, Lyman-alpha/gBAO/SNe/CMB model-combination result, and future Euclid cosmology release have different evidential roles.

## Repair

- `EU-0012-DESI-BAO-LIKELIHOOD` now keeps official DESI product custody but no longer absorbs the extended dynamic-dark-energy interpretation ref as acquired evidence-unit source credit.
- `DF-0021-DESI-LYA-EUCLID-SPECTRA-STAGING-REPLAY` adds a required replay surface for source staging, Lyman-alpha split, model-comparison, and Euclid runway status.
- `ED-0027-DESI-LYA-EUCLID-SPECTRA-STAGING-PRESSURE` makes the staging and interpretation burden route-facing.
- `DX-0004-DESI-LATE-TIME-DARK-ENERGY-DYNAMICS` now hooks the new delta and keeps all outcomes capped at `S2`.
- `tools/cosmology_source_role_policy.py` enforces the split between acquired DESI chain/likelihood custody and interpretation/runway pressure.

## Non-promotion rule

DESI DR2 and follow-up Lyman-alpha/dark-energy analyses remain valuable late-time-expansion pressure, but they are many-to-one cosmology likelihood/model-comparison records. They do not provide unique dark-energy ontology, unreleased spectra/redshift custody, candidate-native ToE derivation, or route promotion.
