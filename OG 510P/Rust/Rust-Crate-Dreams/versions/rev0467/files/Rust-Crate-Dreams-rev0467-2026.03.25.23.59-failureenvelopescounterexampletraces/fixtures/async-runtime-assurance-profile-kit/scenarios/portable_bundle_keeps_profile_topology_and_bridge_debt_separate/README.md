# Scenario: portable bundle keeps runtime profile, service topology, and bridge debt separate

A realistic product may have one host-side Tokio lane, one target-side Embassy or RTIC lane, and one adapter layer to consume crates with different trait/context assumptions.
The right export is one bundle that keeps runtime family, service topology, and bridge debt separate rather than flattening the whole system into one runtime label.
