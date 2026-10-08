# Context-pack release freshness audit

The context pack is a restart surface, not a scientific surface. It must not lag behind the release manifest or revision receipt.

The generated audit checks selected context-pack release fields against `RELEASE-MANIFEST.json` and `REVISION-RECEIPT.json`, including revision, timestamp, bundle, latest release fields, and current revision labels.

A freshness pass does not promote any route; it only reduces restart drift.
