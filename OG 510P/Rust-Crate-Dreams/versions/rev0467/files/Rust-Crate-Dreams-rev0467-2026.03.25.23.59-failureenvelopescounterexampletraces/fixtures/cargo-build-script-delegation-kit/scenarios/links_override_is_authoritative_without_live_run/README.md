# Scenario: `links` override is authoritative without a live build-script run

A distro or workspace config injects metadata for a `links = "foo"` crate.
The build script is not compiled or run, but the resulting metadata is still authoritative for support.
