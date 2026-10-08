# Scenario: docs.rs target shift changes current visibility without rewriting freeze-time basis

A starter-set decision was frozen before docs.rs changed its default target set.
The current hosted docs landing page now tells a different support story than it did at freeze time.

This scenario exists to prove that:

- public docs visibility can drift later,
- replay should surface that drift explicitly,
- and visibility drift alone does not automatically replace the originally chosen crate.
