# OQ-0266 isolated semantic pilot

This runnable pilot replaces co-visible fixed-order packets with four opaque one-arm responder bundles, a hard all-response batch barrier, and a preanswer commitment that fixes the hidden assignment, scoring/admissibility policy, and exact responder-visible packet projections before any responder answers. The execution surfaces are intentionally split:

- Prefreeze dispatch kit: `cloudtainer/oq0266-isolated-semantic-pilot/prefreeze-dispatch-kit.zip` (`d53b12dbefd99337b049ae5e4b334debdc4f2a4738ee605b264dbcffb44fe2b4`). This is the only pilot-wide kit allowed before all responses freeze.
- Postfreeze batch kit: `cloudtainer/oq0266-isolated-semantic-pilot/postfreeze-batch-kit.zip` (`b2b452ed2b9d6f0b7b3902eab1f7f6b6ac356fa9e09bb5b2d3feabc3cf5b347d`). Open only after the dispatch tool emits the exact response-set lock.

The full DelayBasin cube, this builder source, and the postfreeze kit reveal mapping/scoring material and are **not prefreeze-safe**. A collector should open only the prefreeze dispatch kit, distribute one nested responder ZIP per distinct responder, lock all four returned response bytes, then verify the newly opened postfreeze kit against the preanswer policy commitment before handing control to custody/scoring.

Responder bundles:
- `arm-7f2c`: `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-7f2c/responder-bundle.zip` (`7abdc5e1a6398fd84684f8aec719d5b9617713dd772f09d513fa63beb9ca0285`)
- `arm-b91e`: `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-b91e/responder-bundle.zip` (`267d883f39b91deb1a6bddef534707c43005e9eead8b25ceb842fde62becc89a`)
- `arm-d4a7`: `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-d4a7/responder-bundle.zip` (`35d00e6cba879a0160190a0b7818500b4ddcf9d22ec2bdd5ffedf267a61faa21`)
- `arm-e263`: `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-e263/responder-bundle.zip` (`73dd5d1928963c1cbe8bd25a5522d1474dd32d4f587a2a6e8b6615ff93027f91`)

The final evidence capsule binds both source kits and every dynamic artifact, and its outer SHA-256 must be preserved separately before scoring. Replay no longer depends on mutable ambient pilot files. The pilot can supply cleaner isolated semantic evidence. It cannot identify causal burden from one different responder per arm, cannot prove real-world identity separation or trusted time, cannot confirm a global compact default, and cannot replace the still-missing conventional external OQ-0266 triplet.
