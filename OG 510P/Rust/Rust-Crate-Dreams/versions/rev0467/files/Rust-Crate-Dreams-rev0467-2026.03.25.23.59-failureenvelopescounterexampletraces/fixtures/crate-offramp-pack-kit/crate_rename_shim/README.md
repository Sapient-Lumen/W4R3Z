# crate_rename_shim

This scenario exists to keep **redirect/shim availability** separate from **a checked migration path**.

A crate can re-export a successor and still leave downstream users without a witnessed dependency rename, import rewrite, or feature-mapping story.
