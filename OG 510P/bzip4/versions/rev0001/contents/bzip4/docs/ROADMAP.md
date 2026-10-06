# Roadmap

## rev0001 — Huntstag

Strict C++20 compatibility baseline, RAII API, hardening fixes, benchmark/probe tools, upstream differential tests, and research plan.

## rev0002 — measurement and corpus intake

- machine-readable benchmark records;
- corpus manifest with hashes and train/holdout labels;
- richer source/text structure signals;
- peak-RSS collection and optional Linux performance counters;
- boundary/property tests and fuzz harness entry points.

## rev0003 — long-range prototype

- fixed-chunk dedup control;
- content-defined chunking prototype;
- exact collision verification;
- bounded and global dictionaries;
- experimental, explicitly versioned container framing.

## rev0004 — similarity and source structure

- reversible file/record ordering;
- source lexical lane experiment;
- metadata accounting and holdout evaluation;
- combined ordering/dedup ablation tests.

## rev0005 — structured records

- JSONL/log splitter prototypes;
- schema/template dictionaries;
- random-field isolation;
- malformed-input pass-through and strict modes.

## rev0006 — binary analysis

- ELF section inventory and entropy report;
- reversible section splitter;
- relocation/address delta experiments;
- no execution launcher until transform value and decoder safety are proven.

The roadmap is evidence-driven. Corpus measurements can reorder or eliminate tracks.
