# Regression fixture contract gate — rev0067

rev0067 continues from rev0066 without promoting a new private packet. The strict/front lane remains frozen at seven production-gated maintainer packets.

## Purpose

The archived-source gates now prove source intake, Git provenance, clean-room replay, patch application, split-patch attribution, patch order, traceability, and hunk/preimage binding. rev0067 closes a remaining reviewer-facing gap: the exported clean-room regression fixtures themselves.

The new gate asks whether a reviewer can trust the clean-room test bundle as a contract:

- are the exported clean-room tests byte-for-byte the intended maintainer regression artifacts;
- are the exported split patches byte-for-byte the intended rev0059 patch files;
- do the tests avoid cube-private paths and helper imports;
- does the runner pin the expected uploaded source bundle and run with isolated pytest/plugin/cache behavior;
- do synthetic missing/tampered/unsafe states fail closed.

## Results

```text
source bundle used: yes
source SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
fixture lineage rows: 7/7 pass
patch lineage rows: 12/12 pass
runner contract checks: 11/11 pass
negative controls: 5/5 pass
package hygiene rows: 5/5 pass
inherited rev0066 hunk/preimage helper rerun: pass
```

The PB-01 fixed regression imports `socket`; rev0067 keeps this as an allowed, documented exception because the test uses local fake socket stand-ins/constants rather than network I/O. No other clean-room fixed regression uses that exception.

## Files to open

```text
data/rev0067_regression_fixture_contract.csv
data/rev0067_cleanroom_patch_lineage.csv
data/rev0067_runner_contract_checks.csv
data/rev0067_fixture_negative_controls.csv
evidence/rev0067-fixture-contract-helper-output.json
handoff/rev0067/REGRESSION-FIXTURE-CONTRACT-GATE.md
tools/probe_rev0067_regression_fixture_contract.py
```

## Boundary

This is archived-source clean-room fixture-contract evidence. It does not claim live-current upstream filing readiness; the fresh current checkout/tarball gate remains separate and pending.
