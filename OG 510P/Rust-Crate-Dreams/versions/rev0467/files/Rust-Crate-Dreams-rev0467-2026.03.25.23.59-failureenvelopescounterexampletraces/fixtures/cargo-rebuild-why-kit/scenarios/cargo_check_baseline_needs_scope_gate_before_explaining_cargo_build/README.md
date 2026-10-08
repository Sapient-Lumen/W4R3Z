# Scenario — cargo check baseline needs scope gate before explaining cargo build

A nearby `cargo check` session exists, but the incident under review is a fuller `cargo build` run.
The rebuild bundle must record that the baseline is useful context yet only partially comparable.
The point is not to deny the comparison entirely; the point is to stop the bundle from quietly presenting command-family drift as though it were ordinary same-lane rebuild evidence.
