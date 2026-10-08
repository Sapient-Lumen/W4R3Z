# Strip audit — Datacube rev0144 to Lacuna rev0145

## Input custody

Parent artifact:

```text
Datacube-rev0144-2026.06.22.19.25-replay-base-consent-refusal-corpus-audit-custody(1).zip
SHA-256: abcc6993df0ad971f57cc26853004bed49cec24edb5b5ce30b1064d1363ef643
```

The parent contained 662 archive entries and a mature C++20 self-bearing continuation/release system. It supplied valuable engineering instincts—typed transitions, provenance, no-clobber behavior, explicit refusal, replay, custody, and verification—but its operational body was much larger than the epistemic kernel now required.

The parent ZIP is lineage, not vendored runtime content. No parent source file was silently presented as surviving code in this revision.

## What was preserved as doctrine

| Parent strength | Lacuna expression |
|---|---|
| typed transitions | enumerated, validated operations and events |
| replay | deterministic projection rebuild from events |
| custody | immutable event ledger and provenance sources |
| refusal | structured `lacuna.refusal.v1` receipts |
| no-clobber | nonempty initialization refusal and stale-head binding |
| auditability | event/change-set receipts, snapshots, verification |
| explicit nonclaims | verifier and threat-model boundaries |

## What was removed from the runtime

### Self-building and toolchain custody

Removed native compiler detection, ABI/toolchain handling, source capsules, and self-compilation paths. These solve artifact continuation, not epistemic state.

### Release and sidecar machinery

Removed release assembly, package sidecars, transport manifests, and continuation packaging. Revision packaging remains an outer workflow; it is not part of a world ledger's semantics.

### Operational profiling and benchmarks

Removed operation timing/profiling and handoff benchmark surfaces. They may return as external development tools, never as truth-bearing runtime state.

### Cloud/container orchestration

Removed cloudtainer and deployment concerns. Hosting policy is orthogonal to the data model.

### Historical documentation corpus

Removed hundreds of accumulated revision documents from the distributable runtime. Their presence made the artifact self-descriptive but obscured the active contract. This revision carries only current doctrine, decisions, architecture, research, threat model, and lineage.

### Native executable payload

Removed the supplied ELF continuation binary. Lacuna uses a transparent Python launcher and standard-library implementation in this cut so the semantic model can change rapidly and be audited line by line.

## What was not carried forward automatically

No claim is made that every parent behavior has a Lacuna equivalent. This is a product cutover, not a source-level refactor. Features were admitted only when they served semantic custody directly.

## New center of gravity

Rev0145 introduces distinctions the parent did not make the primary runtime abstraction:

- proposition versus assertion;
- assertor versus perspective holder;
- observed versus reported versus inferred;
- accepted versus anchored;
- ledger time versus narrative valid time;
- public versus private versus restricted knowledge;
- one evidence record versus multiple candidate worlds;
- selected hypothesis versus canon;
- missing data versus an explicit open question.

## Re-entry rule

A removed subsystem may return only outside the kernel, or after a revision demonstrates all of the following:

1. it protects an epistemic invariant;
2. it cannot be cleanly implemented by an outer tool;
3. its failure mode is explicit and testable;
4. it does not make the cube responsible for building or deploying itself;
5. its data can be replayed or reconstructed from a stable contract.
