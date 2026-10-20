# ADR 0346: Index tree-v2 directory ancestors during manifest validation

Status: accepted. Implemented 2026-09-09.

## Context

After ADR 0345 grouped merge/projection path work, manifest validation still performed repeated
canonical-manifest searches to prove that every live nested path had a live directory ancestor. For
large nested trees, that made validation spend work proportional to entries times path depth times
repeated binary-search ranges.

The rule itself is simple and unchanged: a live file or directory below `a/b/...` is valid only when
each parent path has at least one directory entry in the same manifest. A file, tombstone, or absent
parent is not enough.

## Decision

Build a set of directory paths during the first validation pass and use that set for ancestor
checks in the second pass.

The validator still performs the same checks:

- namespace policy and engine validity;
- manifest quota, byte, and canonical ordering limits;
- valid path syntax and writer/generation identity;
- per-path duplicate-writer and candidate-count limits;
- file digest/size/owner-mode constraints; and
- live nested ancestor refusal unless each ancestor path has a directory candidate.

No manifest format, branch signature, merge, projection, authority, or storage rule changes.

## Consequences

This removes another repeated lookup loop from large nested tree-v2 operations while preserving the
same accept/refuse boundary. It is an implementation optimization only. IoTox still needs true
path-level incremental scanning/projection and larger Sandwurm capacity repetition before ordinary
large-directory guidance changes.

## Evidence

The owned unit/integration registry now directly checks:

- a nested file with complete directory ancestors is accepted;
- a nested directory/file with a missing parent directory is refused; and
- a nested file whose parent path is a file, not a directory, is refused.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
