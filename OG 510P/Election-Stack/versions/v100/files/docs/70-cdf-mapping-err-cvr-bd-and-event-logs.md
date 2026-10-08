# CDF mapping: BD ↔ CVR ↔ ERR ↔ event logs (closing the audit loop)

**Track:** A (Deployable core)


> **Problem:** many “secure” systems cannot reproduce published results because identifiers, geography, or ballot styles don’t line up across data sets.

This doc defines the **mapping manifest** that binds:
- Ballot Definition (BD)
- Cast Vote Records (CVR)
- Election Results Reporting (ERR)
- Election Event Logging (EEL)

…and makes the relationships reproducible.

## Recommended base standards
- BD: NIST SP 1500-20 (Ballot Definition CDF)
- CVR: NIST SP 1500-103 (Cast Vote Records CDF)
- ERR: NIST SP 1500-100r2 (Election Results CDF)
- EEL: NIST SP 1500-101 (Election Event Logging CDF)
- Guidance across CDFs: NIST GCR 24-058

## Canonical identifiers
### Geopolitical / reporting units
- Use stable `gp_unit_id` values with external identifiers where possible.
- Maintain a `ReportingUnitMap` so precinct splits/merges are explicit, signed, and anchored.

### Ballot styles
- Every CVR MUST reference:
  - `ballot_style_id`
  - `bd_hash` (hash of canonical ballot definition bytes)

### Contests and options
- Contest IDs and option IDs MUST be stable across BD, CVR, and ERR.
- Write-in handling must be pre-specified and consistent.

## Mapping manifest
Introduce `CDFMappingManifest` (content-addressed, signed):
- `bd_hash`
- `cvr_schema_version`, `err_schema_version`, `eel_schema_version`
- `ballot_style_map[]`: style → gp_units
- `contest_map[]`: bd_contest_id → err_contest_id (should be identity unless transformation is justified)
- `option_map[]`: bd_option_id → err_option_id
- `reporting_unit_map[]`: gp_unit relationships and any changes

The manifest MUST be:
- generated deterministically
- canonicalized (e.g., RFC 8785 for JSON)
- included in the EPB

## Minimum reproducibility tests
A verifier MUST be able to:
1. Load BD + manifest
2. Validate CVR references (style/contest/option IDs)
3. Tabulate CVRs into totals
4. Compare totals to ERR in CRO
5. Produce a signed `ReproducibilityReport`

## Privacy and disclosure
Mapping manifests can leak sensitive structure (e.g., very small reporting units). The DisclosurePolicy must specify:
- whether unit-level identifiers are public
- minimum cell sizes
- allowed aggregation levels