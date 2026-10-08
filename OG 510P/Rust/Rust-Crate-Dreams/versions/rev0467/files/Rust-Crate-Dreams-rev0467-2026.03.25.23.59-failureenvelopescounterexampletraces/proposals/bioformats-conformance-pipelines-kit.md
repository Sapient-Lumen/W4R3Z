---
id: P-0187
title: Bioformats Conformance & Pipelines Kit
status: idea
domains: [bioinformatics, data, formats, tooling, conformance, reliability]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/noodles
  - https://docs.rs/noodles
  - https://combine-lab.github.io/blog/2022/11/28/rust-for-bioinformatics-part-2.html
---

# Problem

Rust bioinformatics is growing, but a lot of production work still relies on:

- heavy C bindings (e.g., htslib wrappers),
- one-off format assumptions (BAM/CRAM/VCF edge cases),
- and pipelines that are hard to make reproducible across machines and versions.

The ecosystem has strong building blocks (e.g., `noodles` as a pure-Rust format stack; `rust-htslib` for bindings),
but lacks a **conformance + pipeline evidence** layer that helps teams trust ETL and analyses at scale.

# What it should provide

## A. Format conformance profiles

Named profiles that correspond to real-world constraints:

- `bam-strict` vs `bam-lenient` (what you accept, what you normalize),
- `cram-ref-required` and `cram-ref-embedded` expectations,
- VCF/BCF normalization policy,
- indexing semantics (CSI/tabix edge cases).

Each profile includes:
- “must reject” and “must accept” corpora,
- normalization rules,
- and a machine-readable policy file.

## B. A portable `*.biobundle.zip` evidence bundle

A single artifact for “this file/pipeline broke”:

- `report.json` (formats, versions, profile, verdicts)
- `inputs/` (small samples or hashed references; support remote references)
- `checks/` (validation logs, normalization diffs)
- `replay/` (commands and seeds to reproduce)
- `env/` (reference genome identifiers, refget/htsget endpoints used)

## C. `cargo bio …` UX (for data + pipelines)

- `cargo bio check --profile bam-strict reads.bam` — validate and emit `biobundle.zip`.
- `cargo bio normalize --profile vcf-canonical` — deterministic normalization with diffs.
- `cargo bio etl --spec pipeline.toml` — run an ETL spec and emit evidence bundles per stage.
- `cargo bio diff a.biobundle.zip b.biobundle.zip` — regression detection.

# MVP (ship in weeks)

- `biobundle.zip` schema and minimal validator runner.
- BAM + VCF validation wrappers using existing Rust crates (pure-Rust where possible).
- A tiny curated corpus (edge cases) and a harness to add more.

# v1 (ship in months)

- Broader format surface (CRAM + BCF + indexing formats).
- Remote reference support (refget/htsget) with caching and replay.
- Corpus growth tooling and minimization (reduce failing samples while preserving failure).
- CI integration patterns for research labs and production pipelines.

# Design constraints / risks

- Data size: bundles must support “hashed references” and tiny minimization samples.
- Bio correctness disputes: the kit should separate “profile policy” from engine behavior.
- Community alignment: keep adapters thin; upstream improvements back into `noodles`/friends.
