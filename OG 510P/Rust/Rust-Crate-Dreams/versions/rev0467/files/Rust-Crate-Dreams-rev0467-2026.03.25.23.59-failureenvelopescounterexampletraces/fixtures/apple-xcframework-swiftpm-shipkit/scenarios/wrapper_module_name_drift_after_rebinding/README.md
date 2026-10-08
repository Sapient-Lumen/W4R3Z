# Scenario: wrapper module name drift after rebinding

The XCFramework was rebuilt after a module/modulemap change, but the Swift package wrapper still points at the old binary-target identity.

This scenario exists to keep the shipkit from flattening:
- “the XCFramework was rebuilt successfully”,
- “the wrapper still exists”,
- and “the wrapper still names the same binary target correctly”

into one fake release-valid result.
