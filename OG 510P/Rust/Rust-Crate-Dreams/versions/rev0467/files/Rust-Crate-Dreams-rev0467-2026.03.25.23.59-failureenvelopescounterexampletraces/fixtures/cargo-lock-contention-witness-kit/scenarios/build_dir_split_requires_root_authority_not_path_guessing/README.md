# Scenario: build-dir split requires root authority, not path guessing

The workspace sets a dedicated `build.build-dir`, but the receiver only looked at `target/` and guessed everything was shared.
The bundle must preserve where each root claim came from instead of flattening target-dir and build-dir into one path story.
