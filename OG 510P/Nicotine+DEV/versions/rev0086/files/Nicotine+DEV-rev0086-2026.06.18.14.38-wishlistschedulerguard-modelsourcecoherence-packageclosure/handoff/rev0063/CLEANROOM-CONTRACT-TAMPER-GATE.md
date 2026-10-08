# rev0063 clean-room contract/tamper handoff

Use this together with `handoff/rev0062/cleanroom-kit/README.md`.

rev0063 validates the clean-room kit as a small external artifact contract:

```text
required files: runner + README + 12 split patches + 7 fixed regressions
patch scope: relative paths under pynicotine/
source input: uploaded archived Nicotine-source(1).zip only
negative controls: wrong source, missing patch, unsafe patch path, tampered manifest hash
```

Run the gate from the cube root:

```bash
python tools/probe_rev0063_cleanroom_contract.py --source-zip /path/to/Nicotine-source.zip
```

For a full positive replay, still use the rev0062 runner:

```bash
python handoff/rev0062/cleanroom-kit/run_cleanroom_replay.py \
  --source-zip /path/to/Nicotine-source.zip \
  --kit-dir handoff/rev0062/cleanroom-kit \
  --out-dir /tmp/rev0062-cleanroom-output \
  --lanes all
```

This gate is archived-source evidence only. It is not a substitute for a fresh current checkout/tarball gate before live-current filing.
