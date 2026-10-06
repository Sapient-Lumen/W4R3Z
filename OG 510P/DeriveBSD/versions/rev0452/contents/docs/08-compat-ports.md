# Compatibility: ports / pkgsrc

We want breadth quickly without inheriting nondeterminism forever.

## Strategy

- Build an importer/adapter that translates common ports/pkgsrc patterns into Derive Plans.
- Run builds inside the Derive sandbox and record all impurities.
- Gradually replace “imported” packages with native Derive specs.

## Success metric

A package can graduate from “imported” to “native” without breaking users,
because the external interface stays stable (closure + service integration).


Last updated: 2026-02-23
