# Scenario: AAR native-library collision requires policy

This scenario models a Rust-built Android AAR that packages native libraries in a way that could collide with other packaged JNI libraries in the final app graph.

It exists to keep the crate honest about Android’s own AAR/native-library packaging guidance:

- multiple JNI libraries in one AAR may require explicit collision policy,
- shared runtime libraries like `libc++_shared.so` can create surprising behavior when multiple copies land in one app,
- and a build artifact can be *packaged* without yet being honestly *load-ready*.

The expected outcome is a `load-doctor.report` with a warning or `manual_review_required`, not false certainty.
