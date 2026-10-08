# rev0063 clean-room contract and tamper gate

rev0063 continues from rev0062 and does **not** open a new private packet. The turn adds a fail-closed contract layer around the external clean-room replay kit.

The uploaded source bundle remains the archived source input:

```text
source bundle: /mnt/data/Nicotine-source(1).zip
source sha256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
lanes: github-tag-3.3.10, github-branch-3.3.x, github-branch-master
```

## What this gate adds

rev0062 proved that the clean-room kit could replay the selected strict/front patches and fixed regressions outside the cube. rev0063 adds the complementary contract checks:

```text
1. the exported kit has the expected runner, patches, tests, and README;
2. patch headers remain relative and scoped to pynicotine/ source files;
3. copied regression tests do not import from cube-only maintainer_artifacts/tools paths;
4. the kit contains no symlinks or cache payloads;
5. an inherited rev0062 clean-room replay smoke still passes against the uploaded source;
6. deliberate wrong-source, missing-patch, unsafe-patch, and tampered-manifest controls fail closed.
```

This is deliberately not a new positive vulnerability proof. It is a reviewer-safety layer for the already exported clean-room kit.

## Primary outputs

```text
tools/probe_rev0063_cleanroom_contract.py
data/rev0063_cleanroom_contract_manifest.csv/json
data/rev0063_cleanroom_contract_checks.csv/json
data/rev0063_cleanroom_negative_controls.csv/json
data/rev0063_cleanroom_contract_summary.json
evidence/rev0063-cleanroom-contract-gate/
handoff/rev0063/CLEANROOM-CONTRACT-TAMPER-GATE.md
```

## Status

```text
strict report-candidates: 7
production-gated maintainer packets: 7
new private packets in rev0063: 0
source bundle used: yes
fresh current checkout completed: no
```

Boundary retained: this is archived-source clean-room contract proof. A fresh current upstream checkout/tarball and current-source seven-gate rerun remain separate live-filing requirements.
