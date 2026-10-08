# CELL-038 — Data-Constrained Diffusion-vs-AR Toy LM

Priority: **P2**  
Status: `candidate`  
Idea: `IDEA-0038`  
Sources: SRC-0084, SRC-0085, SRC-0075

## Question

Are diffusion-style language models more sample-efficient than AR on tiny symbolic corpora, or is that claim scale/data-distribution dependent?

## Cheap first run

Tiny grammar dataset; compare masked denoising vs AR under 1k/10k/100k examples.

## Baselines

- random or identity baseline
- strong simple heuristic
- matched-budget architecture baseline

## Metrics

- accuracy/exact match
- loss/error
- memory bytes
- runtime
- failure mode count
- seed variance
- sample_efficiency
- generation_validity

## Stop condition

If diffusion training is too slow on CPU, shelve.
