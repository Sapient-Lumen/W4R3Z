# wiremock_mockserver_is_per_test_fresh_not_shareable_fixture

This scenario captures the boundary documented by `wiremock` itself:

- each `MockServer` is isolated,
- but `MockServer`s should not be shared between tests if you want full isolation and no cross-test interference.

The point is not “wiremock is good”.
The point is that a crate-authored test-support contract should say whether a helper is actually fresh per test or only stays honest when every test constructs its own instance.
