# Scenario — stored call routes can keep old code alive after reload

Chaud explicitly documents that function pointers and trait objects are ways old code can continue to run even after hot reload.

So a compile-iteration bundle should not treat “reload completed” as equivalent to “all call paths now reach fresh code.”
It needs a stale-code-risk artifact for stored call routes.
