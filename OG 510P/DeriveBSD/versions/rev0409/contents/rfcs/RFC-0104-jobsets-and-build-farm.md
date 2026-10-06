# RFC-0104: Jobsets + build farm orchestration

Status: Draft

## Summary

Introduce a DeriveBSD-native “jobset” abstraction for continuous evaluation/build/test/promotion into channels, inspired by Hydra’s operational model.

## Motivation

Hydra’s project/jobset model is a proven way to continuously populate caches and produce release artifacts.
DeriveBSD should steal the abstraction while keeping evaluation deterministic and schema-driven.

## Design sketch

- jobset definition (canonical JSON):
  - source revision selection
  - target matrix
  - policy profile
  - promotion rules
- produce `evaluation.receipt` + promotion manifests
- integrate with builder pools and evidence gates

## References

- Hydra repo docs (projects/jobsets): https://github.com/NixOS/hydra
- NixOS wiki: Hydra overview: https://wiki.nixos.org/wiki/Hydra
- Dolstra paper (Hydra design): https://edolstra.github.io/pubs/hydra-scp-submitted.pdf

