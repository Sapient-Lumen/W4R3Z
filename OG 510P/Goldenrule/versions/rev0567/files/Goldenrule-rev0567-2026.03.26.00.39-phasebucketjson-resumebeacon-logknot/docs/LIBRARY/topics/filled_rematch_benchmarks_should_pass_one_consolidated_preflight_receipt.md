# Filled rematch benchmarks should pass one consolidated preflight receipt

## Claim

Before publishing the first endogenous rematch-world benchmark, the inheritor should run one consolidated preflight receipt that:

1. compiles the compact fill patch if that is the current scratch surface,
2. checks that only the seed edit surface changed,
3. checks that all real world-dependent fill blockers are cleared,
4. confirms the copied compact decision bundle still matches the standing contract, and
5. emits stable digests that can be cited in later handoff notes.

## Why this matters

The archive already had all the underlying pieces, but publication still required remembering a small ritual: compile the patch, run the mutation guard, run the completion gate, and then infer whether the copied decision bundle was still the same object. One consolidated preflight gate keeps the final step small and repeatable.

## Compactness consequence

A consolidated receipt is cheaper than another descriptive benchmark report family. It adds one machine-readable summary and one short inheritor note while reducing the chance that future sessions create new “almost ready” sidecars instead of publishing the standing one-artifact benchmark.
