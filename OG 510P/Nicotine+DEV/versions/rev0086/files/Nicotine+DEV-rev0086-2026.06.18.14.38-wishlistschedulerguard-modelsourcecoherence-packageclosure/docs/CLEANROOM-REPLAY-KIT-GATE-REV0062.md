# rev0062 clean-room replay kit gate

rev0062 continues from rev0061 and does not promote a new private packet. The strict/front lane remains frozen at seven production-gated maintainer packets.

## Purpose

Prior revisions proved traceability, baseline delta, patch roundtrip, patch attribution, and patch-order safety inside the compact cube. rev0062 adds an external clean-room layer: copy the reviewer-facing patches and tests into a minimal kit, move that kit into a temporary directory outside the cube, extract clean source lanes from the uploaded source bundle, apply the exported bundle patches, and run the copied fixed-behavior regressions from the copied kit.

## Added kit

```text
handoff/rev0062/cleanroom-kit/
  README.md
  run_cleanroom_replay.py
  patches/<lane>/*.patch
  tests/u123/*.py
  tests/pb01/*.py
  tests/search-resp-01/*.py
```

The kit intentionally contains only the files required to replay the selected strict/front gates against the uploaded archived source bundle. It does not embed upstream source trees.

## Full clean-room evidence

```text
source bundle: /mnt/data/Nicotine-source(1).zip
source SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
source lanes: github-tag-3.3.10, github-branch-3.3.x, github-branch-master
patch apply rows: 12/12 pass
patched source-file hash rows: 15/15 pass
fixed-regression rows: 21/21 pass
```

The seven fixed regressions passed in the clean-room replay for all three archived lanes.

## Smoke helper

The package helper validates the kit shape and performs a one-lane smoke replay by default:

```bash
python tools/probe_rev0062_cleanroom_replay.py --source-zip /path/to/Nicotine-source.zip
```

For full local replay, use:

```bash
python tools/probe_rev0062_cleanroom_replay.py \
  --source-zip /path/to/Nicotine-source.zip \
  --out-dir /tmp/rev0062-cleanroom-full \
  --lanes all
```

## Boundary

This is archived-source clean-room replay proof against the uploaded source bundle. It still does not replace the live-current checkout/tarball gate before external filing.
