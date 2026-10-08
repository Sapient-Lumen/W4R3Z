# Scenario — scraped visibility requires docs.rs flags and is not local-run proof

A crate opts into scraped examples for docs.rs with unstable rustdoc flags.
The hosted documentation shows an example call-site, but that visibility alone does not prove the local quickstart was run in the same lane.

This fixture keeps these truths separate:

- docs.rs/rustdoc visibility,
- scrape configuration basis,
- and local run success witnesses.
