# Mechanistic and algorithmic probes

Core sources: `SRC-0017` through `SRC-0026`, `SRC-0055` through `SRC-0059`.

## Why this lane matters

Tiny models are scientifically valuable when we can inspect them. Exact synthetic tasks let us ask whether a model has learned a program, a brittle interpolation, a hidden-state basin, or a useful geometric representation.

## Candidate tests

- decompile small length-generalizing models into program-like subcircuits;
- compare softmax, sparse attention, and positional encodings under train-short/eval-long tasks;
- install fact memories and test hidden-state margins vs entropy;
- run modular arithmetic / structured-output grokking side labs;
- test whether dynamic short convolutions accelerate induction/retrieval circuit formation.
