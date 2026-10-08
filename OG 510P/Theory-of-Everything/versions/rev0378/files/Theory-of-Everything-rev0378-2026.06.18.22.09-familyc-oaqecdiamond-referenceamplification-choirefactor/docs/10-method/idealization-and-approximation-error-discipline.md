# Idealization and approximation-error discipline

`OQ-0073` owns the rule that a result in an idealized model is not automatically a result about the physical or candidate-native target.

The archive now distinguishes:

```text
model target
idealized target
finite physical target
candidate-native target
observed-sector target
public-record target
```

An idealization row must say what was deliberately simplified, omitted, frozen, sent to infinity, treated as continuum, isolated, equilibrated, or represented only in a code subspace. An approximation-error row must then say whether the remaining difference is bounded, estimated, stress-tested, merely asserted small, or uncontrolled.

The practical stop rule is:

```text
exact proof / simulation / benchmark / likelihood in an idealized model
≠ deidealized support
≠ observed-sector recovery
≠ candidate-native identifiability
```

The metadata/provenance wrapper is custody-only. A clean package can improve replay and auditability, but it is not an idealized physical model and cannot supply approximation-error bounds.
