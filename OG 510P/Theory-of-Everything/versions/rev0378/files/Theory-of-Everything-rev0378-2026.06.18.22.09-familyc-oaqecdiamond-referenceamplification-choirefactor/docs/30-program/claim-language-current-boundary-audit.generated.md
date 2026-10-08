# Claim-language current-boundary audit (generated)

Generated from `CLAIM-LANGUAGE-PERMISSION-LEDGER.json` and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit directly; run `make index` after changing claim-language rows.

- Route rows: `13`
- Claim-language rows: `14`
- Route-specific claim-language rows checked: `13`
- Conditional current-boundary rows checked: `3`
- Multi-route claim-language rows checked: `1`
- Claim-language current-boundary failures: `0`

## Rule

A route with `authority_state` below `promotion_ceiling` may name the higher ceiling only as conditional future language. Its claim-language permission row must declare the current state, declare the conditional ceiling, include current-vs-conditional qualifiers, forbid unqualified current use of the higher ceiling, and avoid bare `maximum S# wording` phrasing.

## Failures

None.

## Checked rows

| language permission | route | checks | failures |
|---|---:|---:|---:|
| `LPP-0001-FAMILYC-EW-CODE` | `R-OQ0057-FAMILYC-EW-CODE` | `4` | `0` |
| `LPP-0002-FAMILYC-LEARNED-INVERSE` | `R-OQ0057-FAMILYC-LEARNED-INVERSE` | `4` | `0` |
| `LPP-0003-FAMILYB-THERMO-ENTROPIC` | `R-OQ0057-FAMILYB-THERMO-ENTROPIC` | `4` | `0` |
| `LPP-0004-STRINGM-ATLAS` | `R-OQ0057-STRINGM-ATLAS` | `4` | `0` |
| `LPP-0005-ASYMPTOTIC-SAFETY` | `R-OQ0057-ASYMPTOTIC-SAFETY` | `4` | `0` |
| `LPP-0006-CAUSAL-SET` | `R-OQ0057-CAUSAL-SET` | `10` | `0` |
| `LPP-0007-AMPLITUDES-BOOTSTRAP` | `R-OQ0057-AMPLITUDES-BOOTSTRAP` | `4` | `0` |
| `LPP-0008-LAB-GIE-BMV` | `R-OQ0057-LAB-GIE-BMV` | `10` | `0` |
| `LPP-0009-GW-STRONGFIELD-GR` | `R-OQ0057-GW-STRONGFIELD-GR` | `4` | `0` |
| `LPP-0010-FRAME-QRF-RELATIONAL` | `R-OQ0057-FRAME-QRF-RELATIONAL` | `4` | `0` |
| `LPP-0011-LAB-GRAVITON-COUNTING` | `R-OQ0057-LAB-GRAVITON-COUNTING` | `10` | `0` |
| `LPP-0012-COSMO-DARK-ENERGY-BAO` | `R-OQ0057-COSMO-DARK-ENERGY-BAO` | `4` | `0` |
| `LPP-0013-PRIMORDIAL-TENSOR-BMODES` | `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` | `4` | `0` |
| `LPP-0014-METADATA-PROVENANCE-WRAPPER` | `<multi-route>` | `1` | `0` |
