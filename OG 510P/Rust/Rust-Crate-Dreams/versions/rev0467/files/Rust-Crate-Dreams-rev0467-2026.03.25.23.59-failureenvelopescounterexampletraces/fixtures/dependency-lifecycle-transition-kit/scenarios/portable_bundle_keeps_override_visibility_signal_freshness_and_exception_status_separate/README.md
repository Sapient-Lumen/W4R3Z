# Scenario: portable bundle keeps override visibility, signal freshness, and exception status separate

This fixture protects against one fake lifecycle packet where:

- a local patch,
- an old imported signal,
- and an expired waiver

are all summarized as if the dependency transition were still healthy.
