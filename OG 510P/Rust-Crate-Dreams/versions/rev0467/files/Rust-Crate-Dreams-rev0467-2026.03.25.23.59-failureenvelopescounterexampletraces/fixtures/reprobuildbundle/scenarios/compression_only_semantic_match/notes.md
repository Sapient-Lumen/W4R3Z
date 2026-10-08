# Scenario — compression-only drift yields semantic reproduction

The rebuilt `.crate` archive differs byte-for-byte because the compressor produced different archive-level details.
After allowed normalization, the contained file tree and file digests match.

This scenario demonstrates why `semantically-reproduced` should exist as a first-class verdict rather than being flattened into either success or failure.
