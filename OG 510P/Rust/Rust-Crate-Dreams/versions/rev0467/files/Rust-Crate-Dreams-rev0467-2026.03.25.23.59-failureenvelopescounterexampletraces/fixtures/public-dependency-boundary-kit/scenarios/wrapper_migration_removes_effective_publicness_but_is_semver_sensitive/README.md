# Scenario: wrapper migration removes effective publicness but is semver-sensitive

The crate previously returned a dependency error type directly and now wraps it.
The migration plan must keep two truths visible at once: the boundary shrank, and that shrink can itself be SemVer-sensitive for downstream users.
