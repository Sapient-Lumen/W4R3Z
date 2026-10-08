# rev0088 — design-family candidate schema firewall

rev0088 hardens the adaptive-candidate firewall introduced in rev0087.

The risky gap was future-facing: rev0087 correctly rejected `public_counter_life20_stabilizer`, but its primary family was a fixed three-row set. If a later adaptive candidate added another holdout or transfer sampling design, that design could have been absorbed only by the `overall` row while the Bonferroni denominator stayed at three.

rev0088 changes the gate to discover sampling designs dynamically:

- `overall`
- every observed `sampling_design` slice
- known legacy labels for `selected_cell_seed_disjoint_holdout` and `adaptive_candidate_transfer_seedpaired`
- `design:<name>` labels for new/unknown designs

The current rev0084 stabilizer data still has exactly three groups, so the numerical rejection is unchanged. The value is that the next adaptive candidate cannot silently reduce the family size.

A separate row-contract audit now requires adaptive game rows to carry explicit `False` values for both pool-eligibility fields and complete adaptive provenance fields. Missing flags are no longer treated as a harmless absence of leakage.

Current result:

- 240 paired-delta rows audited
- 480 source game rows audited
- 3 family groups
- 6 gate component rows
- 4 schema-contract rows
- 0 schema hard failures
- stabilizer remains rejected by score-transfer and mechanism-drift hard failures
