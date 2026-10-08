# Explicit package selection overrides workspace defaults

This scenario demonstrates that a lane can widen past ambient workspace defaults, but it should do so with an explicit **lane-selection receipt** instead of leaving reviewers to infer that from raw command lines.

The pack should say:

- the workspace had narrower `default-members`,
- the maintainer explicitly selected additional packages,
- feature activation widened accordingly,
- and target coverage beyond the default member came from explicit package selection rather than ambient workspace behavior.
