# Scenario — published extract keeps the release-pair baseline exact

This scenario captures an upgrade lane reviewed against a published crate baseline rather than an already-edited local workspace.

Why it matters:
- a release-pair contract should be able to say the checked baseline came from a pinned published release or package extract,
- a pristine extract should stay distinct from a mutable working tree that already contains local edits,
- and the pack should be able to say its public claims remain safe as a release-to-release contract rather than only as a local migration note.
