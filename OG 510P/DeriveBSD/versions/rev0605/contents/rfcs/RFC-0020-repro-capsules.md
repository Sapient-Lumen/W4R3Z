# RFC-0020: Repro capsules (minimal reproducibility payloads)

Status: Draft

## Summary

Define a small, shareable **repro capsule** format to make build failures reproducible without shipping secrets.

See `docs/39-repro-capsules.md`.

## Goals

- Enable bug reports, CI triage, and explainable “why it failed”.
- Keep capsules small: refer to sources by digest; never embed secrets.

## Capsule contents (v1)

- Spec/Lock/Plan (or digests + retrieval pointers)
- builder base digest + toolchain digests
- structured logs (JSONL)
- normalization knobs
- optional backend mapping outputs

## Non-goals

- shipping full source trees
- including private keys or decrypted secrets
