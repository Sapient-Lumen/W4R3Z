# rev0037 C++ no-choice segment benchmark

rev0031/rev0032 proved that C++ can carry state across no-choice forced segments under Python pre/post SIGv2 checks.  rev0037 adds a small benchmark comparing two C++ transport shapes over the same forced-action traffic.

```text
one-action micro batch:
  one C++ output signature per forced action

segment batch:
  one C++ output signature per no-choice forced run
```

Both are still one coarse subprocess call in the benchmark.  This is not measuring per-action subprocess overhead.  It is measuring the kernel/transport shape after batching.

## Smoke result

```text
games:                         48
segments:                   3,237
forced actions:             8,415
segment C++ seconds:        0.2341
one-action C++ seconds:     0.3009
segment mismatches:             0
skipped events:                 0
estimated compression:       1.52x
```

The one-action path reports more records per second because it emits many more short outputs.  The more useful operational number here is total time for the same forced-action traffic: the segment path was faster and emitted fewer output rows.

## Pushback

This still does not make C++ authoritative.  Python remains the semantic reference and supplies the expected end signatures.  Segment execution becomes a candidate acceleration seam only if it continues passing parity gates on broader traffic.
