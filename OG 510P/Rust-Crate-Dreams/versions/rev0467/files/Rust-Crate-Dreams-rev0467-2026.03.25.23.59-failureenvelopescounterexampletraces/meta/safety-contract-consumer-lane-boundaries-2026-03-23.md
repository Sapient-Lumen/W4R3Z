# Lane boundaries — safety-contract authority, consumer coverage, and semantic lanes (2026-03-23)

Do not let this lane collapse into a fake “contracts are supported” story.

## This lane now owns

**P-0453 Safety Contract Consumer Kit** should now own, in addition to contract snapshots/diffs/runtime receipts:

- contract-clause authority,
- consumer coverage by tool or mode,
- and semantic-lane posture.

That means it owns artifacts such as:

- `contract-authority.receipt.json`
- `consumer-coverage.matrix.json`
- `semantic-lane.report.json`

## Distinct from contract-language or compiler-design work

This lane does **not** own the contract syntax, semantics, or stabilization plan for compiler-native contract attributes.
It consumes that surface.

## Distinct from proof engines and verifier internals

Kani, Creusot, Flux, VeriFast, and other tools own their actual proof/checking/search semantics.
`P-0453` should only own the receiver-facing layer that says:

- what contract surface was imported,
- what each consumer actually covered,
- and what semantic lane fences the result.

Do not turn this into a faux-universal verifier wrapper.

## Distinct from unsafe-audit or assurance-case work

Unsafe-audit lanes inventory unsafe obligations and witness drift.
Assurance-case lanes assemble higher-level claims and evidence.
`P-0453` is narrower: it is about contract consumption truth before those higher layers aggregate it.

## Anti-flattening warnings

Do not let any of these masquerade as an honest answer:

- “contracts were extracted”,
- “Kani passed”,
- “the std fork accepts multiple tools”,
- “the function has a requires/ensures pair”,
- or “runtime checks were green”.

A support story can contain all of those truths and still fail to say:

- which clauses came from what authority,
- which clauses were only partially consumed,
- which semantic lane the result belongs to,
- and what assumptions or boundedness still fence the result.
