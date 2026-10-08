# Scenario: Mixed host Tokio and target Embassy lanes need one honest bundle, not one uniform runtime story

A project uses Tokio in host-side tests/support tools and Embassy on the target firmware lane.
The right exported artifact is one bundle with multiple runtime lanes, not one flattened statement that “the project uses runtime X”.
