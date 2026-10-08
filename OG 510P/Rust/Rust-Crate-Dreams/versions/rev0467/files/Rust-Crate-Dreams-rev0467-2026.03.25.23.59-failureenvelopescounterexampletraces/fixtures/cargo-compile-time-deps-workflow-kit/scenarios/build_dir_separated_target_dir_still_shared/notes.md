# Scenario: build-dir separated target-dir still shared

A rust-analyzer workflow uses a dedicated target-dir subdirectory, but the build-dir lane is still shared with terminal Cargo or not proven isolated. The receipt should preserve that asymmetry instead of treating `targetDir = true` as full root independence.
