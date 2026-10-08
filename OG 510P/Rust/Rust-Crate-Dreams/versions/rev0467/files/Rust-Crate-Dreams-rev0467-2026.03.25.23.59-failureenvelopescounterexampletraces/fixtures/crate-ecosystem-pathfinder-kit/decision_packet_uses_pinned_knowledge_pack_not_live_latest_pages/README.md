# Scenario — a decision packet uses a pinned knowledge pack, not live `latest` pages

Question:
- when pathfinder recommends a starter stack, does the packet point at a pinned review packet, or does it silently rely on floating docs.rs / crates.io latest pages?

Why this belongs here:
- a decision packet is most useful when it can be reopened later and still show the exact support basis it used at decision time.
- docs.rs `latest` and semver routes are good browsing aids, but they are not the same as replayable evidence.
- crates.io Security tab and publication-time surfaces are useful inputs, but they still need pinned import or capture context.

Expected packet behavior:
- the pathfinder packet should reference a knowledge review packet by exact version or frozen bundle identifier;
- the review packet should carry pinned citation locators and answer-boundary notes;
- the decision packet may include human-facing links, but those should be clearly marked as browse routes rather than replay basis;
- re-evaluation should be a separate workflow using replay and reconsideration policies, not a silent swap to current pages.

What this scenario guards against:
- a starter-set bundle that cannot be audited later;
- decision drift caused by `latest` docs pages changing underneath the packet;
- confusing helpful browse links with exact decision evidence;
- pretending that “we can always re-check later” is the same as shipping a replayable packet now.

Relevant sources:
- docs.rs rustdoc JSON
- docs.rs builds
- crates.io development update
- Cargo plumbing commands
- Rust project goals overview
