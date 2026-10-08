# Scenario: docs.rs download keeps format-version and rebuild-gap posture explicit

A docs.rs rustdoc JSON download is a real import route.
It is still not the same thing as a fresh local nightly generation lane.

This scenario keeps explicit:

- docs.rs endpoint authority,
- observed `format_version`,
- compression / redirect posture,
- and the fact that older release coverage can still be incomplete until rebuilds reach that release.
