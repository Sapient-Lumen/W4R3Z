# First endogenous rematch benchmarks should distill one tiny evidence packet before compiling the fill patch

## Claim

When a real endogenous rematch-world benchmark finally runs, the retained archive should keep one tiny evidence packet containing only the world-dependent facts needed by the standing fill patch, and should let bulky traces or temporary run tables remain scratch-only.

## Why it matters

The archive now has a seed, a tiny mutable fill patch, a compile-back step, a mutation guard, a completion gate, and a one-command publication preflight. The remaining risk is that a real benchmark run could still leave behind a bulky family of temporary trace files or hand-edited sidecars before the inheritor distills the final benchmark artifact.

A compact evidence packet fixes that workflow gap. It gives the inheritor one retained object that is smaller than the full seed, excludes the copied decision bundle entirely, and compiles directly into the already-standard fill patch shape. That keeps raw benchmark output in scratch space and keeps the long-term archive focused on distilled facts, schemas, validators, and receipts.

## Operational consequence

Future sessions should:

1. run the real rematch-world benchmark however they need in scratch space,
2. distill the world semantics, matching semantics, occupancy rows, turnover rows, and paired-ranking rows into one tiny evidence packet,
3. compile that packet into the standard fill patch,
4. compile the patch back onto the standing seed,
5. run the consolidated publication preflight, and
6. retain only the final benchmark artifact plus the compact receipt needed for citation.

## Minimal retained objects

- one evidence packet during distillation,
- one compiled fill patch if it is still needed for intermediate review,
- one final filled benchmark artifact,
- one preflight receipt.

Everything bulkier than that can stay scratch-only unless a later archival pass shows that some temporary artifact is genuinely decision-critical.
