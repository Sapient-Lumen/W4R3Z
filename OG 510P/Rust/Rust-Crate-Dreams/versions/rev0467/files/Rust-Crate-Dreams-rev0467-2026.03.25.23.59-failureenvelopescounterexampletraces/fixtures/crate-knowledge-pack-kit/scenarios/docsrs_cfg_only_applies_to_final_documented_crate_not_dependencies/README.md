# Scenario: `cfg(docsrs)` only applies to the final documented crate, not dependencies

Problem:
A maintainer or downstream tool sees `#[cfg(docsrs)]` in one crate and is about to assume that dependencies or workspace peers share the same docs-only visibility posture.

What this scenario proves:
Conditioned availability must record that the `docsrs` cfg scope is limited to the final rustdoc invocation.

Good outcome:
The bundle marks the subject as recipe-bound and records the scope caveat explicitly instead of publishing a fake workspace-wide availability claim.
