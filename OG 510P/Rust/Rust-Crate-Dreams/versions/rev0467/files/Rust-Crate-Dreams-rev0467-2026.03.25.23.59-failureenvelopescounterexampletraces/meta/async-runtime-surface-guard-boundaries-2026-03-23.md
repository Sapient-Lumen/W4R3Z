# Lane boundaries — async runtime deployment topology and surface guards (2026-03-23)

Do not let this lane collapse into a fake “async support across platforms” story.

## This lane now owns

**P-0532 Async Runtime Assurance Profile Kit** should now own, in addition to runtime profiles and service topology:

- deployment-lane identity,
- capability availability by lane,
- and explicit guards around public support claims.

That means it owns artifacts such as:

- `runtime-deployment-topology.receipt.json`
- `capability-availability.matrix.json`
- `surface-guard.report.json`

## Distinct from `P-0484 Toolchain & Target Support Contract Kit`

`P-0484` is about whether the crate/project supports building, documenting, and testing against targets/toolchains at all.

`P-0532` is narrower and later-stage here:

- once a lane exists,
- what runtime family it uses,
- what async capabilities it actually has,
- and what guards fence those claims.

Do not turn runtime-assurance matrices into a full target-support matrix.

## Distinct from service topology and capability routes inside P-0532

The earlier async-runtime refinement already owns:

- where services come from,
- and what route enables one capability.

This refinement adds a different layer:

- **which deployment lane** the claim applies to,
- **whether the capability is available there at all**,
- and **which guard fences the public support claim**.

Do not flatten those into one receipt.

## Distinct from lifecycle/shutdown work

Shutdown semantics, cancellation posture, drain behavior, and timeout aftermath remain lifecycle territory.
A lane can have honest deployment topology and still have poor shutdown semantics.

## Distinct from observability or diagnosis work

A capability matrix is not a symptom map, telemetry recipe, or diagnosis playbook.
It only says what runtime-dependent capabilities are present and under what guards.

## Anti-flattening warnings

Do not let any of these masquerade as an honest answer:

- “the crate uses Tokio”,
- “the examples run on PC”,
- “the docs mention Unix signals”,
- “Embassy has a std example”,
- “a Windows `ctrl_c` demo passed”,
- or “the target firmware uses async”.

A support story can contain all of those truths and still fail to say:

- which lane the claim belongs to,
- which capabilities are absent,
- which claims are platform-specific,
- and which runtime-context/provider guards remain in force.
