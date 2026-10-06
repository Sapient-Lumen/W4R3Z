# Validation indexes, check maps, and admission-coverage honesty

## Practice / observation

DelayBasin has accumulated a large checked command surface.
That is mostly a strength.
`make lint` now acts like a real admission gate rather than a decorative style command.

But that strength created a smaller continuity gap.
A later careful pass can honestly say “lint passed” while still having to spelunk `tools/` to understand what the gate was actually covering.
That is good enough for admission.
It is not good enough for discovery.

The archive now has compact current-state packets, basis witnesses, status-lane witnesses, and a frontier ticket.
What it still lacked was one small surface saying what the checked command surface is broadly doing, what it refreshes directly, and what major validation families sit behind the wrapper.

## Pressure from neighboring datacubes

Several neighboring datacubes apply pressure here.

`EvidenceVault-rev0584` keeps `VALIDATION_INDEX.*` as an explicit inventory of what the checked wrappers prove and refresh, which pressures DelayBasin not to let `make lint` become an opaque prestige green light.
`SlopOS-rev0616` keeps family contracts and harness surfaces explicit, which pressures DelayBasin to say what broad check families exist rather than letting the `tools/` directory itself become the only map.
`Hyperepo-rev0290` keeps manifest and receipt surfaces close to packaging truth, which pressures DelayBasin to say what generators and package-adjacent commands actually materialize the derivative surfaces it relies on.
`Micromax-rev0523` keeps tiny operator-facing surfaces behaviorally honest, which pressures DelayBasin to keep any validation map compact, truthful about its limits, and visibly subordinate to the stronger governing surfaces.

The shared pressure is not “import a lint court.”
The shared pressure is that once an archive already has a large admission wrapper, it may deserve one compact **validation index / check map / admission-coverage note**.

## Working synthesis

DelayBasin should import only the smallest take:

- keep one compact `VALIDATION-INDEX.json` plus one human-facing `docs/00-meta/validation-index.md`,
- let that surface name the major command wrappers,
- let it say what generated surfaces those commands directly refresh,
- let it group the `make lint` tool stack into a small number of broad validation families,
- and let it carry one explicit coverage-honesty note saying that the index is a discovery surface, not a proof graph for every fine semantic distinction.

The point is not to replace `make lint`.
The point is to keep the admission wrapper from becoming a black box for the next careful pass.

## Validation index vs lint vs workflow-state machine

- **`make lint`** remains the admission wrapper.
- **`VALIDATION-INDEX.json`** says what major command surfaces and validation families sit behind that wrapper.
- **`docs/00-meta/validation-index.md`** is the shortest human-facing guide to the same map.
- **A stronger lint court / coverage dashboard / proof graph** would classify and adjudicate much more than DelayBasin has earned.

So the new surface is not a replacement for the admission gate, not a replacement for canon, and not permission to grow a workflow-state controller.
It is a compact discovery map for the checked command surface.

## Design consequences

When DelayBasin keeps a validation index, it should preserve:

- the **derivative status / explicit non-authority note**,
- the **major command surfaces** rather than every remembered shell habit,
- the **directly generated surfaces** those commands refresh,
- the **main validation families** behind `make lint`,
- one explicit **coverage-honesty note** saying the map is broad rather than theorem-complete,
- and the **governing surface hints** a later operator should reopen before inheriting stronger claims.

If the inventory drifts away from the actual checked command surface, it should fail closed and be regenerated.

## Countermodels / probes

Possible failure modes are straightforward:

- the inventory becomes an aspirational dashboard rather than a checked map,
- it starts pretending to answer every per-check semantic question,
- the archive quietly routes real workflow authority through the index rather than through canon and the receipts,
- or the inventory grows so wide that it recreates the `tools/` directory in prose.

Those are reasons to narrow the index or retire it, not reasons to skip a bounded discovery map entirely.

## Transformer-facing implication

If DelayBasin is partly functioning as a bounded continuation substrate, then continuity quality depends not only on what law and state are preserved, but also on whether the archive exposes an honest small map of the admission surface that guards those states.

The weaker implication is not that DelayBasin has discovered a full assurance operating system.
It is this:

**long-horizon archive prompting may benefit from one explicit derivative validation index that keeps `make lint` inspectable as a checked admission surface without pretending that one compact map replaces the underlying contracts, generators, or canon.**
