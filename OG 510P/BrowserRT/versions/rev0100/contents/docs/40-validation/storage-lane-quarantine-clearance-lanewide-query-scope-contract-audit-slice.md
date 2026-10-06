# Storage-lane quarantine clearance lane-wide query scope contract audit

Current in rev0087: `facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit`.

This audit is a wiring guard for the rev0087 lane-wide query-scope slice.  It checks that runtime code treats `allowLaneWide` as lane-scoped in clearance receipt query and replay lookup paths, that release-light and browser proofs exist, and that manifest, impact map, surface inventory, first-read docs, package scripts, Makefile targets, and changelog point at the current rev0087 proof.

The audit does not launch Chromium and does not prove storage durability.  It exists to keep the runtime hardening from drifting out of the cube surfaces.
