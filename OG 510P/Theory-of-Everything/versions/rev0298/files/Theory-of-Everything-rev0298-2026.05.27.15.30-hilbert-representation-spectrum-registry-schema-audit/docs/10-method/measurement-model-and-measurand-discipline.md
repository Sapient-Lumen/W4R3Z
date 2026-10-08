# Measurement-model and measurand discipline

Revision: `rev0267`
Owner ledgers: `MEASUREMENT-MODEL-LEDGER.json`, `SYSTEMATIC-UNCERTAINTY-LEDGER.json`, `CALIBRATION-TRACEABILITY-LEDGER.json`
Open question: `OQ-0064`

A public record is not yet an evidential observable. The archive now requires an explicit measurement model before a route may spend likelihood, update, catalog, benchmark, proof-survival, or support language.

The minimum object is:

```text
raw / formal / detector / catalog / benchmark record
  -> measurand or recoverand
  -> transformation model
  -> correction model
  -> uncertainty expression
  -> candidate-native gap
  -> maximum authority effect
```

This applies to empirical routes and to formal or computational routes. In a lab route, the measurand may be phase, mass, timing, spin/path correlation, or trigger rate. In a gravitational-wave route, it may be calibrated strain and waveform-test statistics. In a CMB route, it may be map-derived polarization likelihoods and tensor-to-scalar constraints. In a holographic or asymptotic-safety route, the analogous object is the declared proof, dictionary, truncation, simulator, or benchmark transformation that turns an input object into a claimed observable or recoverand.

The rule is conservative: a measurement-model row can make update language replayable, but it cannot promote a route. It can only identify what is being measured, what model transforms the record, which uncertainties remain, and what candidate-native gap survives.

## Non-promotion rule

```text
public likelihood + public catalog + public code
≠ support

unless the archive names the measurand, transformation model,
correction model, uncertainty expression, traceability chain,
and maximum authority effect.
```

Metadata/provenance rows are explicitly nonmeasurement rows. They can improve custody and replay, but they cannot become physical or candidate-native evidence.
