# ADR 0070: Qualify Ratox R7 with bounded fail-closed evidence

Status: accepted
Date: 2026-08-17

Format note: ADR 0071 supersedes the v1 evidence-file format and provenance boundary. In particular,
v2 removes the asserted `physical-host-count`/`route-observation` labels and the cross-clock local-stage
sum. The qualification thresholds, required route/load cells, and test-sharding decision here remain
in force.

## Context

A two-host latency claim is only useful when the input identifies the complete service path, route
shape, load cell, clock model, and one-input/one-render semantics. An ad hoc spreadsheet or permissive
script could silently accept missing cells, duplicate samples, clock-domain subtraction, malformed
numbers, truncated files, or an unbounded input. Sanitizer runs also need bounded wall time: the owned
registry contains process-heavy cases that should remain one contamination oracle in ordinary builds
but can be split into deterministic shards under instrumentation.

Primary references rechecked for this decision:

```text
https://www.rfc-editor.org/info/rfc6374/
https://cmake.org/cmake/help/latest/command/set_tests_properties.html
https://cmake.org/cmake/help/latest/prop_test/PROCESSORS.html
https://clang.llvm.org/docs/AddressSanitizer.html
https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
```

## Decision

### Canonical evidence contract

`tools/analyze-ratox-r7.py` consumes one ASCII tab-separated file with exact metadata and twelve-field
sample records. Required metadata freezes:

```text
schema=iotox-ratox-r7-samples-v1
service-path=ratox-v1-complete-pty
physical-host-count=2
toxcore-version=0.2.23
randomized=1
controller-clock=steady
host-clock=steady
cross-host-clock-comparison=0
route-observation=verified
```

The complete matrix contains observed `direct-udp` and `forced-tcp` routes beside 0, 1, 8, 16, 32,
and 64 bulk streams. Every cell contains at least 1,000 and at most 10,000 samples. Ordinals are unique,
contiguous, nonzero, and begin at one. Unsigned values are canonical decimal uint64 values without
leading zeroes. End-to-end time is nonzero; local stage sums may not exceed it; every sample must show
exactly one input commit, exactly one render copy, and completion.

The parser bounds metadata count, line length, total bytes, total lines, and per-cell samples. It
rejects carriage returns, non-ASCII bytes, duplicate metadata, unsupported cells, missing cells,
malformed shape, impossible stage sums, and mutation of the input file while it is being read. The
path is opened read-only with close-on-exec, nonblocking, and no-follow flags where available; only a
regular file is accepted. Reports are deterministic text and JSON.

### Qualification gates

Nearest-rank integer percentiles are computed independently for every cell. All route forms require:

```text
owner queue-wait p99 < 2,000 us
zero one-commit/one-render/completeness violations
```

Observed direct UDP additionally requires:

```text
end-to-end p95 <= 50,000 us
end-to-end p99 <= 100,000 us
zero samples >= 250,000 us
```

Forced TCP latency is reported but is not assigned the direct-UDP limits. This prevents the relay path
from being mislabeled as direct while still preserving its measured distribution.

### Test sharding

`IOTOX_TEST_SHARD_COUNT` is a configure-time integer in `1..64`. The default value one preserves the
single monolithic owned-registry contamination oracle. Values above one create deterministic CTest
shards using the registry's existing index/count filter. Every shard is labeled `owned-registry`,
claims one processor, and has a finite timeout. The ASan/UBSan and TSan presets select sixteen shards
to bound individual instrumented processes without weakening the default oracle.

The analyzer's malformed-input matrix is itself a CTest target whenever a Python 3 interpreter is
available.

## Consequences

A passing analyzer report means the supplied canonical matrix satisfies this decision's shape,
semantic, and numeric gates. It does not prove that the metadata is truthful, that two physical hosts
were actually used, that route observation was independently verified, or that clocks were correctly
instrumented. Those facts require retained experiment procedure and raw evidence.

The default suite continues to detect order contamination in one process. Instrumented suites gain
bounded deterministic shards, and invalid shard counts fail at configure time. Python remains an
optional test dependency; absence of the interpreter means the C++ product can build, but no R7
qualification report should be claimed on that host.

## Rejected alternatives

- **Accept CSV, JSON, and arbitrary columns.** Multiple permissive formats enlarge ambiguity and parser
  surface without improving the qualification contract.
- **Allow missing or undersized cells.** A partial matrix cannot support a load-shape claim.
- **Use floating-point percentile interpolation.** The gate must be deterministic and conservative.
- **Apply direct-UDP thresholds to forced TCP.** That conflates route forms and can hide relay-specific
  behavior.
- **Always shard the default registry.** Separate processes would weaken the ordinary order- and
  contamination-sensitive oracle.
- **Treat analyzer PASS as proof of experiment provenance.** A parser validates evidence shape and
  values, not the truth of physical metadata.
