# Scenario: explicit target build splits host-helper scope

The workspace is built with `--target` or `build.target`, so target-specific `rustflags` apply to the target lane.
Host-built build scripts and proc macros remain separate compiler invocations and should not be silently upgraded to the same exercise scope.
