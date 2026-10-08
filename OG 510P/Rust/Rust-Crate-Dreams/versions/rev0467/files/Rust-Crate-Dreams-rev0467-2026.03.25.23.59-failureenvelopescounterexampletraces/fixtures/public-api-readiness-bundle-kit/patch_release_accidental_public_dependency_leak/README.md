# Scenario: patch release accidental public dependency leak

A patch release claims “internal cleanup only,” but a public reexport now exposes a dependency type in the library surface.
The semver story may still look superficially acceptable until the public-boundary report is inspected.
