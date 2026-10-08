# Scenario — dirty workspace baseline blocks release-pair claims

This scenario captures an upgrade lane reviewed inside a mutable workspace that already contains unpublished changes and a partially applied migration.

Why it matters:
- package/feature/target scope can still be exact while the starting subject is not an exact published baseline,
- replayability and config-basis honesty still do not answer whether the lane was checked against the real release pair or against a locally drifted tree,
- and exported summary claims should fail consistency if they pretend the lane is a clean release-to-release contract.
