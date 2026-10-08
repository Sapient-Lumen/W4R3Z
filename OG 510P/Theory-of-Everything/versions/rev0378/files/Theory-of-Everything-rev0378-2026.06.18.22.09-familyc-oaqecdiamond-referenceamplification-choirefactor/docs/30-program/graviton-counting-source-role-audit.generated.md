# Graviton-counting source-role audit (generated)

Generated from route-bearing `*LEDGER.json` rows for `R-OQ0057-LAB-GRAVITON-COUNTING`. Do not edit directly; run `make index` after changing graviton-counting source custody.

- Required core single-graviton rows: `11`
- Missing core single-graviton rows: `0`
- Source-role placements checked: `351`
- Source-role placements displayed: `17`
- Empty/pass placements suppressed: `334`
- Source-role failures: `0`

## Display policy

The full executable check still scans every route-bearing row. This generated restart surface displays only rows with core single-graviton refs, classical trigger refs, LISA/runway refs, failures, or required core-row status, because hundreds of empty passing route rows added noise without changing custody semantics.

| Row | Core single-graviton refs | Classical trigger refs | LISA/runway refs | Passed |
|---|---|---|---|---:|
| `ACQUISITION-PROTOCOL-LEDGER.json:AP-SINGLE-GRAVITON-TRIGGER-CORRELATION` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | `REF-0218` | — | `true` |
| `CALIBRATION-TRACEABILITY-LEDGER.json:CAL-0011-LAB-GRAVITON-COUNTING` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `CLAIM-LANGUAGE-PERMISSION-LEDGER.json:LPP-0011-LAB-GRAVITON-COUNTING` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `CREDIT-ALLOCATION-LEDGER.json:CA-LAB-GRAVITON-COUNTING` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `DECISION-EXPERIMENT-LEDGER.json:DX-0013-GRAVITON-COUNTING-STATE-STATISTICS-CORRIDOR` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | `REF-0624`, `REF-0625` | — | `true` |
| `DISCRIMINATOR-FORECAST-LEDGER.json:R-OQ0057-LAB-GRAVITON-COUNTING` | `REF-0175`, `REF-0647`, `REF-0648` | — | — | `true` |
| `DISCRIMINATOR-FORECAST-LEDGER.json:R-OQ0057-LAB-GRAVITON-COUNTING` | `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `EMPIRICAL-DELTA-LEDGER.json:ED-0006-SINGLE-GRAVITON-STIMULATED-ACCESS` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `EMPIRICAL-DELTA-LEDGER.json:ED-0007-GRAVITON-COUNTING-STATE-TOMOGRAPHY` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `EMPIRICAL-DELTA-LEDGER.json:ED-0018-GRAVITON-REALIZATION-AND-QUANTIZATION-SPLIT-PRESSURE` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `EVIDENCE-SEVERITY-LEDGER.json:SV-0004-GRAVITON-COUNTING-SEVERITY` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `EVIDENCE-UNIT-LEDGER.json:EU-0011-GRAVITON-COUNTING` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `INDEPENDENCE-ASSUMPTION-LEDGER.json:IA-0005-GW-WAVEFORM-DETECTOR-CATALOG-COVARIANCE` | — | `REF-0218` | — | `true` |
| `MEASUREMENT-MODEL-LEDGER.json:MM-0011-LAB-GRAVITON-COUNTING` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `PUBLIC-RECORD-CARRIER-LEDGER.json:PRC-GRAVITON-LAB-CATALOG` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |
| `PUBLIC-RECORD-CARRIER-LEDGER.json:PRC-GWOSC-STRAIN-CATALOG` | — | `REF-0218`, `REF-0624`, `REF-0625`, `REF-0629` | — | `true` |
| `SYSTEMATIC-UNCERTAINTY-LEDGER.json:SYS-0011-LAB-GRAVITON-COUNTING` | `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648` | — | — | `true` |

## Source-role rule

Classical gravitational-wave catalogs may act as source-trigger/timing carriers only on explicitly trigger-bearing rows. LISA mission, construction, or hardware-runway refs must not be spent as detector-local single-graviton/click evidence for the lab graviton-counting route.

## Non-promotion rule

This audit creates no new support. It preserves the distinction between trigger covariance, detector-local transition/count evidence, and ToE-candidate identity.

