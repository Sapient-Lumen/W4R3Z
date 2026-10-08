# Drift program

Web AI surfaces change constantly. GlassTTY needs a deliberate drift program.

## Drift inputs

The repo already has many useful ingredients:
- fixture captures
- probe captures
- smoke reports
- operator handoff bundles
- operator attempt before/after bundles
- comparison reports
- setup ledgers and next-action hints

These should be treated as parts of one program, not as isolated utilities.

## Drift severities

- **informational** — changed shape, no workflow impact observed
- **low-risk** — minor structural change, current workflows still pass
- **degraded** — workflows still partly succeed, but signals or selectors are weakening
- **blocking** — one or more required workflows fail
- **unknown** — evidence is insufficient to classify

## Drift outputs

A useful drift artifact should answer:
- what surface changed?
- which workflows are affected?
- what stable signatures changed?
- what still works?
- what likely broke?
- what should be tried next?

## Operating loop

1. capture baseline
2. capture new evidence
3. compare
4. classify severity
5. update support truth
6. recommend next adapter or policy change
7. preserve the diff in a ledger

## Where the mechanics live

Use `docs/drift-operations.md` for:
- sweep triggers
- artifact expectations
- update responsibilities for support records and ledgers

## Important rule

Do not make future implementers rediscover drift manually through live browser frustration if the repo could have told them from stored evidence.
