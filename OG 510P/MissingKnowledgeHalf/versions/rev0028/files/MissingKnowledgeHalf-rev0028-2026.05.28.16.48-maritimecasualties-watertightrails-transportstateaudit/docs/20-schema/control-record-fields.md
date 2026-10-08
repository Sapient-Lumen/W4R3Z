# Control record fields

Revision: rev0019

`CTL` records are calibration surfaces for pattern candidates. They are not failure records and not celebratory success records. Their purpose is to stop the cube from learning only from cases that already fit a pattern.

A control record should state:

- what pattern it calibrates;
- whether it is a positive control, negative control, counterexample, intercepted/caught-before-harm case, or boundary case;
- why it fits the calibration role;
- what overclaim it prevents;
- what limits keep it from becoming a new myth.

Rev0019 introduces CTL with three positive controls for `MKH-PAT-0015`: APOE ε4, HLA-B*5701/abacavir, and ADH1B/ALDH2.
