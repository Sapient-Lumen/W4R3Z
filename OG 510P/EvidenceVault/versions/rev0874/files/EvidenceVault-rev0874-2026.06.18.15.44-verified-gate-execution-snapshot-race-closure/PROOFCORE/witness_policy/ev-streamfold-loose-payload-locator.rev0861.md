# Witness policy — rev0861 loose payload locator

The verifier may inspect public JSON reports, the streamfold payload manifest, the
locator contract, synthetic self-test fixtures generated in temporary directories,
and the rev0860 parent checkpoint surfaces. It must not require private witness
material, hidden canonical payload bytes, network access, or rights-owner
assertions.

Candidate roots supplied by an operator are outside this overlay. The locator may
scan them only as explicit public inputs to the utility command; the rev0861 lane
certificate itself records the no-candidate-root absence state.
