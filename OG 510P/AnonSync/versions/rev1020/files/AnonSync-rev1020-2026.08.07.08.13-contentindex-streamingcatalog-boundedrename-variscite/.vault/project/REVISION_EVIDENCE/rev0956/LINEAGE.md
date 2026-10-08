# Rev0956 lineage

Parent: `AnonSync-rev0955-2026.07.31.04.28-rotatingscrub-integrityepoch-readinessfence-heliodor.zip`

Parent SHA-256: `fb5de95e59a6832d7dc50e720e82cc5cc184684558343face89fea8dd92c019b`

Package: `AnonSync-rev0956-2026.07.31.12.22-integritystatus-degradedrecovery-ownerproof-peridot.zip`

Rev0956 is reconstructed from the sealed rev0955 parent and the recorded active
source patch. The active projection contains 565 files,
25127088 bytes, and SHA-256 `47895b30aedb76b1e30f924d8a8712812dc473ab381c3d157a62af469c0e1fe8`.

The slice keeps the single C++ product spine and changes payload-integrity
mismatches from daemon-ending events into an owner-visible fail-closed degraded
state. Recovery remains dependent on complete current-byte payload reproof and
ordinary folder convergence.
