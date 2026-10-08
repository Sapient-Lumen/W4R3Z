# Scenario: signed XCFramework with privacy-manifest gap

The published XCFramework is signed and expected to participate in origin verification, but one supported platform slice lacks the expected privacy-manifest inclusion.

This scenario exists to keep the shipkit from flattening:
- “the bundle is signed”,
- “Xcode can reason about origin”,
- and “the third-party-SDK trust posture is fully ready for downstream consumers”

into one fake trust result.
