# Frontier salience refresh — 2026-03-23 (227)

## Main judgment

Do **not** broaden the archive with a large new batch of sector ideas on the next pass.
The next strongest work is to deepen the practical implementation queue for horizontal crates whose upstream substrate is now unusually explicit.

## Practical implementation queue

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0472 Docs.rs Build Parity & Evidence Kit**
4. **P-0489 Cargo Build-Dir Consumer Transition Kit**
5. **P-0535 Dependency Lifecycle Transition Kit**
6. **P-0484 Toolchain & Target Support Contract Kit**
7. **P-0536 Crate Knowledge Pack Kit**
8. **P-0537 Compile Iteration Feedback Kit**

## Why this ordering changed

### P-0509 stays first
Crate choice is still a cross-domain pain and crates.io’s newer surfaces improve raw facts without giving users a receiver-facing decision pack.
The pathfinder lane still has the widest multiplier effect.

### P-0486 stays near the top
Debugging is still one of the clearest ecosystem pain points with fresh official survey attention.
The debuggability lane already has enough substrate to define witnessable capability classes instead of fuzzy “debug support”.

### P-0472 now belongs in the near-term queue
The docs.rs surface is now mature enough that a parity/evidence crate can be sharp rather than speculative:
- hosted limits are documented,
- metadata knobs are documented,
- rustdoc JSON is documented,
- the hosted environment is acknowledged as imperfectly reproducible locally,
- and CI guidance already points maintainers toward preflight testing.

### P-0489 also belongs in the near-term queue
Cargo’s Build Dir Layout v2 testing call makes this a live migration seam rather than a future abstraction debate.
A receiver-facing transition bundle now has a clear job.

### P-0535 and P-0484 remain essential
Safety-critical, regulated, embedded, Wasm, and mixed-language users still need stronger dependency / target / support truth.
But the docs/build/debug queues are slightly more implementation-ready right now.

### P-0536 and P-0537 remain high leverage but no longer the next immediate repo deepening targets
They are still central frontier lanes.
This pass only says that docs/build parity and migration seams now have unusually concrete current pressure and official substrate.

## Promotion / demotion rule

Promote a lane when all three are true:

1. official sources describe the pain clearly,
2. official or de facto substrate exists already,
3. the archive can name a concrete `0.1` artifact set without fantasy leaps.

Demote or defer a lane when it still mostly depends on:

- upstream language changes not yet settled,
- private or unstable integration points with no honest support contract,
- or a value proposition that collapses into “another wrapper”.
