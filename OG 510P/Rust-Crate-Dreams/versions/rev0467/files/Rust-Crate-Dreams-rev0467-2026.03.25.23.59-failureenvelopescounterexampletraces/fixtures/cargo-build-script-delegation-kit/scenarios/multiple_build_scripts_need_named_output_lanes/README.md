# Scenario: multiple build scripts need named output lanes

A crate uses multiple build scripts to split Windows-manifest generation from release-info stamping.
The support question is not only whether both units ran, but which unit exported which `OUT_DIR` and metadata surface.
