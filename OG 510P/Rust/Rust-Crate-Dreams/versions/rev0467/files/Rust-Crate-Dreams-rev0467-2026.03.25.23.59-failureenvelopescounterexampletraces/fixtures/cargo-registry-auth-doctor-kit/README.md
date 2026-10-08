# Cargo Registry Auth Doctor Kit fixtures

Fixture ideas:
- crates.io token-based login with successful index access but publish disabled
- authenticated sparse registry with `auth-required = true` and missing credential provider
- external credential provider returning malformed protocol JSON
- trusted-publishing environment expected for publish but unavailable on one CI runner
