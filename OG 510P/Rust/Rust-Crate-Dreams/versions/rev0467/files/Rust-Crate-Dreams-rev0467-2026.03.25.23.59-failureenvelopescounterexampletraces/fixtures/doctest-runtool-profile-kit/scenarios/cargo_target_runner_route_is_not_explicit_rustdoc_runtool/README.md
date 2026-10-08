# Scenario — Cargo target runner route is not the same as explicit rustdoc `--test-runtool`

This scenario records a target lane where doctests are executed through Cargo target-runner configuration rather than explicit rustdoc `--test-runtool` flags.
The result may still be valid, but the support contract should say *how* the wrapper route was selected.
