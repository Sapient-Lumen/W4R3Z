# Scenario: package-version inference breaks interface match

This scenario models a composition attempt where one component imports an interface without an explicit package version while the available dependency exports the same interface with an explicit version.

It exists to resist a common false conclusion:

> “The names look the same, so composition should obviously work.”

The expected outcome is a world-lock report that records the mismatch instead of forcing reviewers to rediscover it from failed composition logs.
