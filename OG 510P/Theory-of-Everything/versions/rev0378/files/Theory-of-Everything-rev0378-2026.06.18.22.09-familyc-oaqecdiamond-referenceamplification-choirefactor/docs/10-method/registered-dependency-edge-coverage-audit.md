# Registered dependency-edge coverage audit

Introduced in `rev0303`.

The route-support stack now has many registered route-local families. A route row can name a support handle, but the authority graph must also carry the corresponding route dependency edge. This audit checks every registered `route-local-plus-wrapper` family and verifies that every route-field handle has at least one `AUTHORITY-DEPENDENCY-GRAPH.json` edge into the owning route.

This prevents the following refactor failure:

```text
new route-support handle added
+ route rows and schemas know it
+ claim bindings know it
but authority-dependency graph lacks the edge
= hidden rollback / authority propagation gap
```

The generated surface is `docs/30-program/registered-dependency-edge-coverage-audit.generated.md`.
