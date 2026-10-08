# Scenario: env forces internal-build mode

This scenario exists because `system-deps` already supports `SYSTEM_DEPS_$NAME_BUILD_INTERNAL=auto|always|never`.

The worthy crate should not reinvent that substrate. It should freeze the decision into a portable lock/report so another person can see that vendored mode was chosen deliberately, not inferred after the fact from a successful build.
