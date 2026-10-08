# Scenario — README start is official but docs.rs visibility is only partial

A crate blesses one README section as the official “start here” path.
Docs.rs builds with restricted features/targets, so the path is still official but only partially visible on the hosted surface.

This fixture keeps these truths separate:

- a quickstart can be official,
- docs.rs can show only part of it,
- and hosted visibility does not replace a local runnable witness.
