# Scenario — decision packet carries evidence sources, not just rankings

Question:
- when Pathfinder tells another engineer “start here”, what evidence packet rides with that recommendation so the result survives review and later replay?

Why this belongs here:
- the archive increasingly treats Pathfinder as the front door for crate selection,
- but a ranked answer without a replayable basis is still too easy to bluff,
- especially for cross-target, regulated, offline, or mixed-language choices.

Expected packet behavior:
- the decision packet should point to a `basis-lock.manifest.json` and a `review-packet.manifest.json`;
- `candidate-elimination.receipt.json` should cite why other candidates were excluded without turning exclusions into universal anti-recommendations;
- task-fit claims should stay separate from imported trust signals such as trusted publishing posture or advisory surfaces;
- the packet should clearly say what target, publication window, and packaged-state assumptions were in scope.

What this scenario guards against:
- “top crate” rankings that cannot be replayed;
- decisions built from floating `latest` pages;
- cross-target claims that ignore filtered dependency graphs or hosted-doc recipe drift;
- staff-review handoff packets that hide their basis behind prose.

Relevant sources:
- Rust challenges
- 2025 State of Rust survey results
- cargo metadata
- Cargo external tools
- docs.rs rustdoc JSON
- crates.io development update
