# Rematch world benchmark evidence packets should carry one compact scratch provenance receipt

## Claim

A distilled rematch-world evidence packet should be retained together with one compact receipt that hashes the scratch-only source files it came from and records which benchmark sections those scratch files supported.

## Why this matters

The archive already had a seed, a fill patch, a packet compiler, a compile-back step, a mutation guard, a completion gate, and a consolidated publication preflight. What it still lacked was one retained object tying the tiny packet back to the wider scratch material it summarized.

Without that receipt, the workflow still leaned on memory: an inheritor could know that a packet existed, but not which scratch files substantiated it once the bulky traces were removed. A compact receipt fixes that gap without retaining the bulky traces themselves.

## Compactness consequence

A hashed receipt is much cheaper than keeping wide trace bundles in the long-term archive. Future sessions should retain the distilled evidence packet plus one receipt, cite those two objects in the handoff log, and let larger raw traces or temporary tables remain scratch-only unless they become decision-critical.
