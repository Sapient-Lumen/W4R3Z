# rev0062 clean-room replay kit

This folder is intended to be copied outside the cube. It contains only the lane-specific split patches, copied fixed-behavior regression tests, and a standalone runner.

Example:

```bash
python run_cleanroom_replay.py \
  --source-zip /path/to/Nicotine-source.zip \
  --kit-dir . \
  --out-dir /tmp/rev0062-cleanroom-output \
  --lanes all
```

The runner extracts the three archived source lanes from the uploaded source bundle, applies the four filing-bundle patches in canonical order, and runs the seven copied fixed-regression tests from this kit. It does not import tests or helper code from the full cube.
