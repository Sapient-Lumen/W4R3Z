# Credit-allocation current-boundary audit (generated)

Generated from `CREDIT-ALLOCATION-LEDGER.json` and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit directly; run `make index` after changing credit allocation rows.

- Route rows: `13`
- Credit rows: `13`
- Conditional-route credit rows checked: `3`
- Credit-allocation current-boundary checks: `86`
- Credit-allocation current-boundary failures: `0`

## Rule

Credit allocation rows aggregate evidence units, so their prose must name the route's current authority state. A row may retain a higher conditional ceiling only with explicit `current_credit_state`, `conditional_authority_ceiling`, and `conditional_trigger` fields and with text forbidding unqualified current use of the higher ceiling.

## Failures

None.

## Checked rows

| credit row | route | checks | failures |
|---|---:|---:|---:|
| `CA-AMPLITUDES-BOOTSTRAP` | `R-OQ0057-AMPLITUDES-BOOTSTRAP` | `6` | `0` |
| `CA-ASYMPTOTIC-SAFETY` | `R-OQ0057-ASYMPTOTIC-SAFETY` | `6` | `0` |
| `CA-CAUSAL-SET` | `R-OQ0057-CAUSAL-SET` | `6` | `0` |
| `CA-COSMO-DARK-ENERGY-BAO` | `R-OQ0057-COSMO-DARK-ENERGY-BAO` | `6` | `0` |
| `CA-FAMILYB-THERMO-ENTROPIC` | `R-OQ0057-FAMILYB-THERMO-ENTROPIC` | `6` | `0` |
| `CA-FAMILYC-EW-CODE` | `R-OQ0057-FAMILYC-EW-CODE` | `6` | `0` |
| `CA-FAMILYC-LEARNED-INVERSE` | `R-OQ0057-FAMILYC-LEARNED-INVERSE` | `6` | `0` |
| `CA-FRAME-QRF-RELATIONAL` | `R-OQ0057-FRAME-QRF-RELATIONAL` | `6` | `0` |
| `CA-GW-STRONGFIELD-GR` | `R-OQ0057-GW-STRONGFIELD-GR` | `6` | `0` |
| `CA-LAB-GIE-BMV` | `R-OQ0057-LAB-GIE-BMV` | `10` | `0` |
| `CA-LAB-GRAVITON-COUNTING` | `R-OQ0057-LAB-GRAVITON-COUNTING` | `10` | `0` |
| `CA-PRIMORDIAL-TENSOR-BMODES` | `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` | `6` | `0` |
| `CA-STRINGM-ATLAS` | `R-OQ0057-STRINGM-ATLAS` | `6` | `0` |
