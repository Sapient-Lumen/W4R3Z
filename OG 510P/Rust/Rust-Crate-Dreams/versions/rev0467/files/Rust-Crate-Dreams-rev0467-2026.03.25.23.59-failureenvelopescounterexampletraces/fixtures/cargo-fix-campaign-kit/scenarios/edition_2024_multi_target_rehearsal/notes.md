# Scenario: edition 2024 multi-target rehearsal

A workspace needs separate fix passes for:

- the main library and binary targets,
- feature-gated examples,
- and tests that expose edition-compatibility lints only under `--all-targets`.

The campaign is still *rehearse only* because macro-heavy tests remain in manual review.
