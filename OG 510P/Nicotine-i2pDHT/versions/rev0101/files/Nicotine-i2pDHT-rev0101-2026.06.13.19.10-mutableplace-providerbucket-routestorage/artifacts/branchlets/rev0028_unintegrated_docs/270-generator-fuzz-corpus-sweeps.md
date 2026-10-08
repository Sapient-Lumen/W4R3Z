# Generated fuzz corpus sweeps

`fuzzwire.py` pins hand-written malformed fixtures. `generatorfuzz.py` grows that into a deterministic generated rejection corpus.

The generator starts from accepted seed cases and mutates them into known-bad cases across:

```text
parseguard canonical decode
wirecanon frame validation
transportshadow report-frame validation
```

The current mutations cover trailing data, duplicate keys, nesting/depth pressure, appended/truncated wire payloads, and shadow expected-digest drift.

This is not production fuzzing. It is a reproducible baby-corpus that catches accidental accept-by-default drift while the wire shape is still moving.
