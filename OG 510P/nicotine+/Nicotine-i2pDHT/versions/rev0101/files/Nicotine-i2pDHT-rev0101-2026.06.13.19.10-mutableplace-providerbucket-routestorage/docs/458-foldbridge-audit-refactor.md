# Foldbridge audit/refactor

`foldbridge.py` is the rev0044 audit/refactor lane.  It keeps two rev0043 histories visible:

- canonical rev0043: `keycompartment`, `authoritysplit`, `compartmentfold`,
- folded alternate rev0043 branchlet: `controlintent`, `bridgefirewall`, `foldtrim` preserved under `artifacts/branchlets/rev0043_controlintent_bridgefirewall/`.

The audit checks current rev0044 paths, branchlet preservation, predecessor paths, public/head/index needles, foldmap, foldregistry, and surfaceledger.  The goal is not to erase branch debris but to make branch adoption explicit and test-pinned.
