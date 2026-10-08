
# Example doctor note: build-state-pack/contract0

Status: **illustrative witness output**

## Bounded finding
The dominant change between the two captured sessions is not package selection or feature drift.
It is the addition of **experimental build-dir-layout-v2 path observations** in the nightly run.

## What changed
- toolchain changed from `stable-1.94.0` to `nightly-2026-03-15`
- build-dir-layout-v2 observations were introduced only in the nightly run
- stable package graph and build-script counts stayed materially the same

## Likely decision improved
A build steward can now tell the team:
- the path/layout drift is real,
- it is tied to an experimental import,
- and any downstream tool relying on old path inference should be tested before treating the nightly run as representative.

## Caveat
This note is **not** proof that the new layout is stable or final.
It only says the capture/diff surface can preserve the layout caveat explicitly.
