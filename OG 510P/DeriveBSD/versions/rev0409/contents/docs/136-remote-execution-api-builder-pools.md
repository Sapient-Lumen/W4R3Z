# Remote Execution API semantics for builder pools (CAS + ActionCache)

DeriveBSD wants **distributed, hostile builder pools** without inventing a bespoke protocol.
A strong prior art is the Bazel/Remote Execution API ecosystem:
- clients describe an **Action** by digest (command + inputs)
- workers execute in a controlled environment
- outputs are addressed by digest and can be cached

References:
- Remote Execution API repo/spec: https://github.com/bazelbuild/remote-apis
- REAPI v2 proto (Action/Command/CAS/ActionCache): https://github.com/bazelbuild/remote-apis/blob/main/build/bazel/remote/execution/v2/remote_execution.proto

## Lesson to steal

- **CAS is the substrate**: inputs/outputs are blobs + directory trees addressed by digest.
- **ActionCache is explicit**: “this Action digest produced these output digests”.
- **Execution is replayable**: witness rebuilders can re-run the same Action digest.

## DeriveBSD mapping

### Where it plugs in

- **Plan → Artifact** becomes “submit Actions derived from the Plan”.
- the Action digest can be derived from:
  - Plan digest
  - normalized environment digest (toolchain, base image/jail template)
  - declared network policy (deny by default)

### Minimal subset DeriveBSD could adopt

- `ContentAddressableStorage` for blobs + directory trees
- `ActionCache` for reusable results
- `Execution` for remote worker runs

### Why this helps the hostile-builder posture

- workers can be treated as **untrusted**: the client verifies digests, signatures, and required attestations
- action determinism + caching makes **witness rebuilders** cheap

See also:
- `docs/104-builder-tiers.md` (local jail vs microVM builders)
- `docs/118-distributed-builds-pbulk.md` (distributed builds as normal)
- `docs/116-witness-rebuilders-diffoscope.md` (independent rebuild attestations)

Candidate RFC: *REAPI-aligned builder pools + CAS store adapters*.

Last updated: 2026-02-23
