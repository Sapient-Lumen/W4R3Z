# Scenario: credential alias redaction keeps support meaning but breaks public replay

A publish-related command relied on `registry.global-credential-providers` plus a `[credential-alias]` entry whose provider path and arguments include machine-local details.
A public-safe bundle may keep the origin/source-class meaning while redacting the exact provider command, but then it must not claim public replayability.
