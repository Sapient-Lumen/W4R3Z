# Scenario: checksum matches, but simulator slice is missing

The remote SwiftPM binary target points to the expected zip and the checksum is correct, but the XCFramework only ships an iOS device slice.

This scenario exists to keep the shipkit from flattening:
- “the wrapper is valid”,
- “the checksum matches”,
- and “the package fully supports iOS development workflows”

into one fake compatibility result.
