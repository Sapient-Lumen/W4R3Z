# Scenario: weak dependency feature forwarding requires prior activation

A package feature uses `rgb?/serde` alongside `dep:serde`.

Why this matters: the `?/` syntax forwards a dependency feature only if something else already enabled the optional dependency. A resolver bundle should preserve that this clause did **not** itself activate `rgb`, and should say when the explanation is conservative because downstream surfaces or error messages flatten the precondition away.
