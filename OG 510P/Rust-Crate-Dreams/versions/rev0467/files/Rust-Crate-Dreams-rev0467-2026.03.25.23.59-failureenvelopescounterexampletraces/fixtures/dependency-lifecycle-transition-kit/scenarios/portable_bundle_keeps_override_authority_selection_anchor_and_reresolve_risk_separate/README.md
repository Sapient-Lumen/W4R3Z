# Scenario: portable bundle keeps override authority, selection anchor, and re-resolve risk separate

This fixture protects the archive against a common flattening error:

- where a route is declared,
- what currently anchors the route,
- and whether the route survives a fresh resolve

are related, but they are not the same claim.
