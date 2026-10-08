# Release invariants and claim boundaries

A late-stage archive can be internally consistent and still unfinished. This surface records the
invariants that must remain true whenever the archive ships with `FT-0181` live.

The purpose is not to add another proof artifact. The purpose is to keep the archive from slowly
changing the meaning of “ready-but-not-closed” until examples, validators, or release audits are
mistaken for real pilot evidence.

## Invariant states

| Code | Meaning |
|---|---|
| `INV0` | no invariant record exists |
| `INV1` | invariants are prose-only |
| `INV2` | invariants are machine-readable and path-checked |
| `INV3` | invariants are tied to validators, release claims, and forbidden states |
| `INV4` | invariants are reviewed with each release candidate |
| `INVX` | an invariant is contradicted, stale, or used as evidence |

## Default rev0222 invariants

1. A packaged archive may be ready-but-not-closed only when every live followthrough item is named
   and externally gated.
2. `FT-0181` cannot close through schema validity, control coverage, release audit hashes,
   signoff setup, public-summary rendering, or policy exception.
3. Every example JSON must be declared with source status, and `SRC0`/`SRC1` examples must prohibit
   effectiveness claims.
4. Public summaries must stay below source truth, evidence grade, and redaction profile limits.
5. Protected-route facts, raw learner traces, and security payloads must not enter ordinary public
   service records.
6. A real import requires dictionary, acceptance, lifecycle, decision-delta, closeout, quorum,
   control-coverage, audit, and assurance review.
7. A stale external source can downgrade or reopen claims; it cannot silently remain current.
8. A waiver cannot bypass source truth, protected separation, no-fake-import, authority ceilings,
   or public-claim limits.

## Boundary rule

An invariant can block release, block closure, or narrow a public claim. It cannot itself supply
`SRC2+` pilot evidence, prove learning, prove safety, or close `FT-0181`.

## Maintenance rule

When a new validator, schema, example family, or public-summary route is added, update the invariant
record before shipping. If the invariant record is stale, set the release candidate to `RCX` or keep
it internal until the boundary is restored.

See `examples/release-invariants/rev0224-release-invariants.json` and
`tools/check_release_invariants.py`.
