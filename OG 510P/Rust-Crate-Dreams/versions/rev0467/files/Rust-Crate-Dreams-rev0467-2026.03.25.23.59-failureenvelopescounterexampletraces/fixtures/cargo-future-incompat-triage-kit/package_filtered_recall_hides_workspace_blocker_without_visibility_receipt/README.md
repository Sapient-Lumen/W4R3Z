# Scenario — package-filtered recall hides a workspace blocker without visibility receipt

A full workspace capture stored a future-incompatibility blocker in one package.
A later `cargo report future-incompat --package ...` recall is narrower and does not show that blocker.

The bundle must preserve that the later view is a narrowed recall surface, not proof that the workspace-level blocker disappeared.
