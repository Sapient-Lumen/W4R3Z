# CAS everywhere (beyond “binary cache”)

DeriveBSD already has a content-addressed store. The mile-high direction is to treat **every** phase output as CAS-addressed so we can cache, verify, and explain uniformly.

This borrows the “Action Cache + CAS” mental model from build systems like Bazel and BuildStream:
- action key = digest(inputs + metadata)
- action result points at CAS blobs/trees

## DeriveBSD interpretation

- Plan digest is the primary “action key” for builds.
- Output objects (artifacts, closure manifests, proofs, SBOMs, attestations) are stored by digest.
- “Binary cache” becomes a *replication layer* over the CAS with policy on what may be served.

## Why it matters

- fast CI and team reuse without weakening verification
- cheaper “rebuild to verify” because intermediate results are addressable
- enables remote builders that are treated as hostile (verifier checks outputs)

## Non-goals (v1)

- mandating remote execution (optional)
- making the store format identical to any external project

See RFC-0070.
Last updated: 2026-02-23
