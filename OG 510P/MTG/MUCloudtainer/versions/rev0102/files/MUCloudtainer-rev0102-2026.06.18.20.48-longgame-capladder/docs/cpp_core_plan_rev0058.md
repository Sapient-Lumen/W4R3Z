# C++ core plan — rev0058

## Status

No C++ cutover in this revision.

The C++ microkernel remains a parity shadow over Python-owned gameplay.  rev0058 checked `58172` chosen transitions from the decomposition panel:

```text
supported events: 58172
skipped events:   0
mismatches:       0
match rate:       1.0
```

Replay-trace C++ checking also passed:

```text
events:     2495
skipped:    0
mismatches: 0
```

## Retention change

rev0058 does not ship the full transition table.  It ships a compact sample and the summary instead.

This keeps parity confidence while avoiding the historical pattern of adding tens or hundreds of MiB of raw transition CSV per revision.

## Next C++ work

C++ tournament-core cutover remains lower priority than explanatory confirmation.  The next useful C++ improvement is not broader scope; it is a standard compact evidence format:

```text
summary JSON
mismatch rows
unsupported rows
bounded deterministic sample
optional archive-tier full trace
```
