# FT-0080 closure

FT-0080 asked whether aggregate compromise-era and recovery-audit rollups should define publication cadence, cross-operator suppression-threshold equivalence, or statistical-noise / privacy-budget posture.

rev0081 answers yes, but only as aggregate publication-safety metadata.

Closed by:

- adding required `aggregate_summary.aggregate_privacy_controls`,
- defining publication cadence and differencing-risk posture,
- defining digest-bound suppression-threshold equivalence for compatible-operator aggregate cohorts,
- defining statistical-noise posture as policy-bound count semantics without exporting privacy-budget or noise-parameter material,
- adding `aggregate_privacy_control_summary` as a non-satisfying evidence class,
- adding positive and negative fixtures for cadence, threshold equivalence, noise binding, de-suppression, discovery malformation, and evidence-class misuse.

The closure preserves the rule that aggregate privacy controls cannot become profile evidence, current actionability evidence, individual replay visibility, verifier authorization, or TimeSync provenance.
