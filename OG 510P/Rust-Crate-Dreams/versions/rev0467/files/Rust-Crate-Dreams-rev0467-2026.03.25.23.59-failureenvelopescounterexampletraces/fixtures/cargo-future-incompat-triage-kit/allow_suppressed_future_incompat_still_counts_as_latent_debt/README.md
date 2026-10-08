# Scenario — allow-suppressed future incompatibility still counts as latent debt

A dependency emits a future-incompatibility diagnostic that is preserved in machine-readable output,
but the human-facing terminal review path did not show an active warning surface because the warning was suppressed.

The bundle must preserve two truths at once:

- the finding exists and still matters for release debt,
- and the original human review surface did not present it as an ordinary visible blocker.
