# Scenario notes

This scenario exists to prove that **P-0046** is not just a prettier wrapper for `cargo::error`.

The important behavior is that a structured error existed, but a non-zero exit still left the user with a large log dump. The crate should preserve the short actionable fix while demoting directive noise.
