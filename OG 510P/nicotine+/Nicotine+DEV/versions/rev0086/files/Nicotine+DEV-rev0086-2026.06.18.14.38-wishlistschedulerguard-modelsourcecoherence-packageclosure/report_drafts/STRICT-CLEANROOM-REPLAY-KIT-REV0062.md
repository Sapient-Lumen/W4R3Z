# Strict/front clean-room replay kit — rev0062

rev0062 adds an external replay layer for the seven production-gated strict/front packets. The replay kit can be copied outside the cube and run with only the uploaded source bundle.

Core command:

```bash
python handoff/rev0062/cleanroom-kit/run_cleanroom_replay.py \
  --source-zip /path/to/Nicotine-source.zip \
  --kit-dir handoff/rev0062/cleanroom-kit \
  --out-dir /tmp/rev0062-cleanroom-output \
  --lanes all
```

Recorded result in this revision:

```text
patch apply rows: 12/12 pass
patched file hash rows: 15/15 pass
fixed regression rows: 21/21 pass
```

This improves reviewer portability but does not change filing status: live-current upstream checkout/tarball proof remains required before external filing.
