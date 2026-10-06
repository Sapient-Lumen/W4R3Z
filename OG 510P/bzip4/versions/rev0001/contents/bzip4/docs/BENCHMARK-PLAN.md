# Benchmark plan

## Principles

- Hash every input and preserve the exact corpus manifest.
- Compare against the same revision, compiler, flags, block size, worker count, and machine state.
- Separate codec CPU time from disk I/O unless the test is explicitly end-to-end.
- Record both size and resource costs; never report ratio alone.
- Tune on a training subset and report holdout results separately.
- Include incompressible and malformed data so optimizations cannot assume friendly input.

## Corpus families

### Personal text and source

The primary specialist corpus should include representative writing, source, generated files, and revisions. Keep a chronological holdout set that is not used to tune transforms or dictionaries. Record whether files are raw, tarred, sorted, deduplicated, or normalized.

### Version and snapshot structure

Use repeated source trees, release snapshots, generated build outputs, and related archives. Compare:

- raw concatenation;
- filesystem/tar order;
- path order;
- similarity order;
- fixed dedup;
- content-defined dedup;
- dedup plus bzip4.

### General text/code controls

Use stable public corpora such as large encyclopedia text, source trees, and classic compression suites when acquired. Keep exact versions and hashes; do not silently replace a corpus with a newer mirror.

### Structured records

JSONL, CSV, logs, and generated records should cover both consistent schemas and mixed/adversarial inputs. Include UUIDs, timestamps, high-entropy IDs, floats, nested objects, escaping, and malformed records.

### Binaries

Include stripped and unstripped ELF executables, shared libraries, object files, debug-heavy builds, and related versions produced from the same project. Also include already-compressed assets and random bytes as bypass controls.

## Metrics

For every result record:

- input bytes and SHA-256;
- output bytes and SHA-256;
- ratio and bits per input byte;
- encode/decode wall time and CPU time;
- encode/decode MiB/s;
- peak RSS;
- worker count and block size;
- compiler full version and flags;
- CPU model, core count, frequency policy, OS/kernel;
- transform/container version and all parameters;
- successful byte-for-byte verification.

## Baseline commands

```bash
# Structural signal
./build/bzip4_probe corpus.bin > results/corpus.probe.txt

# In-memory block benchmark
./build/bzip4_bench corpus.bin 16 5 > results/corpus.block16.txt
./build/bzip4_bench corpus.bin 64 5 > results/corpus.block64.txt

# End-to-end stream baseline
/usr/bin/time -v ./build/bzip4 -f -b 16 -j 1 corpus.bin corpus.b16.j1.bz3
/usr/bin/time -v ./build/bzip4 -f -b 64 -j 4 corpus.bin corpus.b64.j4.bz3
./build/bzip4 -t -j 4 corpus.b64.j4.bz3
```

## Timing protocol

1. Build Release once and archive the compile command database.
2. Verify CPU governor and thermal state where possible.
3. Run one warm-up not included in the result.
4. Run at least five iterations for short workloads; report median and spread.
5. Alternate candidate/baseline order to reduce thermal or background bias.
6. Use dedicated process affinity only when recorded and applied to both sides.
7. Keep I/O-cold and I/O-warm experiments separate.

## Ratio decision thresholds

There is no universal percentage gate, but the following are useful triage rules:

- under 1%: usually reject unless speed/memory also improves or the change is nearly free;
- 1–5%: potentially valuable for a general codec if costs are modest and consistent;
- 5–15%: strong result requiring broad validation;
- 15–30%: likely structural or domain-specific; investigate generality and metadata carefully;
- 30%+: verify corpus leakage, accidental lossy behavior, omitted metadata, and train/test contamination before celebrating;
- 50%+: plausible for missed long-range or domain structure, not an assumed universal core-codec target.

These are research heuristics, not guarantees.
