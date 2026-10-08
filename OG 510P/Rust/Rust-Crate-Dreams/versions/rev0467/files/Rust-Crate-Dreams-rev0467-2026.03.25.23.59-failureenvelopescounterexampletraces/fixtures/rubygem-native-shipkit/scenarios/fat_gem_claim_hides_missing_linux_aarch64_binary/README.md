# Scenario: fat-gem claim hides missing linux-aarch64 binary

The README and release notes describe the release as a boring precompiled/fat-gem rollout.
In reality the shipped artifacts cover macOS and x86_64 Linux, but omit `aarch64-linux` so that users on that platform still fall back to a local source build.
