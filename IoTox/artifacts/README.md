# Retained lightweight artifacts

The source tree keeps only small, source-referenced receipts here. Build trees,
prebuilt binaries, fuzz executables, CTest logs, standalone attempts, and bulky
revision transcript directories are generated evidence and must live outside the
tracked source tree unless a future decision explicitly promotes a tiny receipt.

Current retained set:

```text
rev0045/tox-tor-smoke.json
rev0045/tox-operator-tor-smoke.json
rev0045/i2p-sam-two-router-smoke.json
rev0045/actual-tor-path-population.json
rev0045/content-lane-counterbalance.json
rev0045/SHA256SUMS
```

These files are route/privacy construction receipts referenced by docs and one
self-test verifier. They are not a current binary release, not a stable release
dossier, and not a substitute for the live Sandwurm/export evidence named in the
roadmap and ship-readiness docs.

Verify the retained rev0045 receipt set with:

```sh
cd artifacts/rev0045
sha256sum -c SHA256SUMS
```

New build and release artifacts should use ignored output locations such as
`build/`, `dist/`, `.sandwurm/`, or `DR0Pbox/`. Public repository datacubes copy
the committed source snapshot and include `dist/standalone/` only when its
recorded `source-commit` matches the exact datacube commit.
