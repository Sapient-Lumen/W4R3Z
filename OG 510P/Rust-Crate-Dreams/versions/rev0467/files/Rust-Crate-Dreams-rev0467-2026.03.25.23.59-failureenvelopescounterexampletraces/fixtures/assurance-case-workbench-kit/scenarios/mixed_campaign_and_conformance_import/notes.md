# mixed_campaign_and_conformance_import

This scenario proves the workbench can assemble one release-facing assurance pack from three different input classes without flattening them:

1. a `verifybundle@1` verification-campaign import,
2. a `conformancebundle@1` protocol/interoperability import,
3. and a manual review note for one unresolved operational assumption.

The expected top-level result is **`manual-review`**, not `satisfied`, because the imported evidence is fresh and parseable but one explicit operational assumption still requires human sign-off.
