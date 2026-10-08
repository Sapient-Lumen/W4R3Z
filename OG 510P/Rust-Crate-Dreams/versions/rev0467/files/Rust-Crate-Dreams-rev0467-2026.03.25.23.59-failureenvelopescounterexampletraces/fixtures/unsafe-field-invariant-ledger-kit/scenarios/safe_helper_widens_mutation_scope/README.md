# Scenario: safe helper widens mutation scope

A crate documents that `len` must never exceed initialized elements, but a new safe helper mutates `len` after a refactor.
The important review fact is not merely “unsafe blocks changed”; it is that the **mutation lane** widened from constructor-only/unsafe-direct to a new trusted-safe-wrapper claim that now requires explicit review.
