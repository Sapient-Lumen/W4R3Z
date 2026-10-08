# Scenario — workspace-wide `--no-default-features` scope needs an explicit receipt

This scenario models a workspace observation where `resolver = "2"` and a workspace-wide command used `--no-default-features`.
The receipt exists to keep that workspace-wide observation from masquerading as a single-package support promise.
