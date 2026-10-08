# Witness policy — ev.pcd.overlay_integrity.rev0853

Policy: `public-only`.

The first rev0853 proof-carrying-data lane does not use a private witness. Verification inspects public files in the extracted overlay bundle: manifest, manifest sidecar, patch filenames, proofcore files, carried canonical index, rights ledger, and fixtures.

A future `zkrtp` or `streamfold` lane may introduce private witnesses. When that happens, witness policy must state whether the witness is retained, redacted, synthetic, regenerated from source, or intentionally unavailable, and it must describe the public commitments that bind to it.
