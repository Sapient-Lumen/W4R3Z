# Optimization hunt

This is the working research map, not a list of promised wins. Every proposed change must be reversible, benchmarked against rev0001, and measured on both its target corpus and unrelated holdout corpora.

## Objective vector

We will track a Pareto frontier rather than optimize one number blindly:

- compressed bytes and bits per input byte;
- encode and decode wall time;
- peak resident memory and allocation volume;
- decoder code size and dependency footprint;
- startup latency for packed executables;
- corruption containment and recoverability;
- deterministic output and reproducible builds;
- compatibility or explicit container-version cost.

A ratio win that consumes unreasonable memory, destroys decoding speed, or only memorizes one training corpus is not a general improvement. It may still be useful as an opt-in specialist mode.

## H0 — instrument before changing the codec

Revision 0001 is the control. The first corpus work should produce:

1. `bzip4_probe` output;
2. `bzip4_bench` results at several block sizes;
3. CLI BZ3v1 archive sizes;
4. wall time, peak RSS, CPU model, compiler flags, and input hashes;
5. a train/holdout split when heuristics will be tuned.

The probe’s current fixed-chunk and duplicate-line signals are intentionally simple. They tell us where to look, not what final transform to build.

## H1 — long-range deduplication before BWT

This is the highest-priority ratio experiment for snapshots, related source trees, generated text, release archives, and repeated templates.

Upstream’s README gives the motivating extreme: the archive of Perl releases compressed to 546,456,978 bytes with bzip3 `-b 511`; long-range deduplication followed by bzip3 produced 60,672,608 bytes. That is evidence that substantial redundancy can live outside the effective visibility of one bzip3 pass.

Candidate design:

- content-defined chunking using a rolling hash or FastCDC-like gear hash;
- chunk fingerprints plus exact byte verification before emitting references;
- bounded dictionary modes for constrained memory;
- reference coding optimized for nearby and repeated chunk IDs;
- optional chunk canonicalization or similarity buckets;
- a manifest that reconstructs the exact byte stream;
- independent checksums for the transform layer and inner BZ3 blocks.

Experiments:

- fixed 4/16/64 KiB chunks as a cheap control;
- content-defined mean sizes from 4 KiB through 1 MiB;
- global dictionary versus sliding-window dictionary;
- minimum-reference savings after metadata overhead;
- dedup-before-ordering versus ordering-before-dedup;
- cross-file dedup with and without tar/container padding normalization.

Failure modes to test include hash collision handling, adversarial all-unique data, memory blowup from tiny chunks, and references spanning damaged regions.

## H2 — similarity ordering with reversible manifests

BWT benefits when related contexts are nearby. Raw filesystem order, timestamp order, or record arrival order is often accidental.

Candidate units:

- files in a source/version archive;
- lines, records, functions, or generated objects;
- JSON objects grouped by schema and event type;
- log records grouped by template;
- binary sections grouped by role.

Candidate fingerprints:

- byte n-gram sketches;
- token shingles for source/text;
- MinHash/SimHash-like signatures;
- prefix/suffix context signatures;
- lightweight entropy and alphabet profiles.

The transform must serialize the original order compactly. Any size win must include permutation metadata. Tests should compare nearest-neighbor heuristics, clustering, stable lexicographic keys, and no-order controls. We should also test whether ordering makes long-range dedup less necessary or more effective.

## H3 — format-aware stream splitting

Mixed fields pollute each other’s models. An opt-in structural transform can separate predictable lanes and recombine them exactly.

Initial targets:

- JSON/JSONL: keys, punctuation/schema, strings, integers, floats, booleans/nulls, timestamps, IDs, and free text;
- CSV/TSV: per-column streams plus row/quoting metadata;
- logs: template IDs, timestamps, severity, host/process IDs, numeric arguments, and residual text;
- source code: lexical classes, identifiers, whitespace/newline layout, comments/strings, numeric literals, and punctuation;
- versioned trees: paths, metadata, manifests, and file payloads.

Rules:

- parsing must be exact and reject or pass through malformed input safely;
- transform metadata counts toward compressed size;
- small inputs should bypass expensive transforms;
- random/high-entropy fields should not poison structured fields;
- decoders must remain bounded and validate every stream length.

A source-specialized mode is especially relevant to the intended personal corpus. It should be tuned on one subset and judged on unseen writing/source to avoid a bespoke dictionary that only compresses training material.

## H4 — BWT and post-coder research

After preprocessing controls, profile the core itself:

- LZP dictionary size, hash, minimum match, and enable/disable decision;
- RLE thresholds and transform ordering;
- context-mixer state layout and probability update rates;
- block-size selection based on entropy and repetition signals;
- BWT suffix-array memory traffic, allocation reuse, and threading;
- alternative reversible BWT post-transforms aimed at redundancy not captured by the current coder;
- arithmetic/range coder renormalization and branch behavior;
- block-local model warm starts versus independent blocks.

Every parameter search needs held-out corpora. A “best” constant found on one text set is likely overfit. Use automated sweeps that save full configurations, input hashes, and compiler identity.

## H5 — binary-aware preprocessing

Generic BWT can compress binaries, but executable structure creates special opportunities:

- split code, read-only data, writable data, relocations, symbols, debug data, and padding;
- normalize relative branches/calls into target-oriented values and reverse them exactly;
- delta-code relocation addresses and symbol/string tables;
- canonicalize zero/alignment gaps while retaining a layout map;
- group repeated templates or function bodies across related builds;
- strip only when explicitly requested, because stripping is lossy with respect to the original file.

Start with analysis-only ELF support. Do not mix the executable launcher with the codec experiment: first prove that a transform produces smaller reversible bytes, then design a safe launch path.

## H6 — implementation and throughput

Ratio work should not obscure straightforward systems improvements:

- profile-guided optimization and link-time optimization;
- allocation pooling and state reuse;
- more cache-friendly context state layouts;
- SIMD only where profiles show meaningful hotspots;
- asynchronous file I/O and larger sequential buffers;
- dynamic scheduling for uneven block costs;
- avoiding oversubscription when libsais or outer jobs use threads;
- architecture-specific builds as optional artifacts, never the only portable path;
- compile-time feature detection instead of hard-coded CPU assumptions.

For constrained environments, decoder memory and binary size may matter more than encoder speed. Maintain separate “small decoder,” “balanced,” and “maximum ratio” profiles if tradeoffs diverge.

## H7 — adaptive and hybrid modes

A generally improved compressor may need to choose rather than force one pipeline:

- cheap classification from entropy, byte histogram, repetition, and text/binary signals;
- bypass for already-compressed/encrypted regions;
- BZ3 core for BWT-friendly blocks;
- specialized transforms only when predicted savings exceed metadata and CPU budgets;
- per-stream/block method flags inside a future container;
- explicit resource ceilings so auto mode cannot surprise constrained users.

The classifier must be evaluated on false-positive cost. A conservative bypass is better than expanding common data or invoking an expensive transform for negligible gain.

## Experiment acceptance gates

A candidate moves beyond a branch experiment only when it has:

- byte-exact round-trip tests, including empty, tiny, boundary, random, and malformed inputs;
- deterministic output or a documented reason otherwise;
- sanitizer and fuzz coverage for decoder-facing parsers;
- measured metadata overhead;
- results on target and holdout corpora;
- peak-memory measurements;
- corruption and truncation behavior;
- a versioned format description if it changes the stream;
- a rollback path and a baseline comparison generated by the same harness.

## Suggested revision sequence

- **rev0002:** corpus intake manifest, richer probe signals, repeatable benchmark result format, compiler/CPU metadata.
- **rev0003:** fixed-chunk and content-defined dedup prototypes in an experimental container.
- **rev0004:** similarity ordering for source trees and line/record corpora.
- **rev0005:** source/JSON/log structural splitter experiments.
- **rev0006:** ELF analysis and reversible section splitting; no launcher yet.
- **rev0007+:** core parameter sweeps, profile-driven throughput work, and a container decision based on measured winners.

The sequence can change when actual corpus evidence points elsewhere.
