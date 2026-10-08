# Rev0952 audit summary

Rev0951 bounded remote effects but not the rooted pathname inspection that
preceded candidate selection. Rev0952 introduces an independent inspection
frontier and a schema-v5 durable sweep journal bound to the exact catalog digest
and replica visible-state digest. Origin, count, and cursor must reproduce one
cyclic coverage sequence across restart. Unresolved status is sticky for the
sweep, and final settlement requires a complete clean sweep.

The complete projection is still restored and hard-validated before effects.
The journal is scheduling/coverage state only: it cannot authorize a path,
payload, predecessor, or publication. Selected rooted owners finish before
progress publication, and any selected effect retires an incomplete pre-effect
sweep. Idle classification cannot bypass a partial sweep or exceed the ordinary
inspection budget.

The audit/refactor also removed an effectively quadratic bulk projection path.
`visible_paths()` no longer copies distinct paths and rescans every active
operation once per path. It groups borrowed immutable operation pointers once by
borrowed canonical path and shares one materializer with `visible_path()`. A
512-path reverse-insertion regression binds canonical ordering and exact primary
identity. Same-path maximality remains pairwise and the complete projection is
still materialized.

Catalog migration v4→v5 retains and re-proves the authenticated local scan
journal and cyclic cursor. Process/configuration tests bind the independent limit,
JSON diagnostics, durable restart continuation, stable completion, missing-
payload deferral, and tampered sweep-state refusal. The structural audit has
74 lexical checks; it is not semantic proof.

Principal remaining costs are complete projection restoration/admission,
asynchronous rather than snapshot-isolated sweeps, rooted local prefix replay,
whole immediate-directory sorting, restart-cold payload inventory, non-atomic
cross-owner cutpoints, append-only retained history, and incomplete product
semantics. See
`BOUNDED_REMOTE_INSPECTION_SWEEP_AND_LINEAR_VISIBLE_PROJECTION_AUDIT_rev0952.md`.
