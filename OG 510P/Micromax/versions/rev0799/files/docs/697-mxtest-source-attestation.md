# mxtest source attestation and resume trust (rev753)

Rev751 made long validation resumable, and rev752 made completed manifests useful for future scheduling. Rev753 closes the next trust gap: a resumed chunk was guarded by ordered node ids, but source files could change while collected node ids stayed identical. That made it possible for `--resume` to skip a chunk whose previous pass belonged to a different source tree.

## Source manifest

Every normal mxtest plan/run now embeds a source attestation:

```json
{
  "source_digest": "...",
  "source_file_count": 700,
  "source_total_bytes": 1234567,
  "source_manifest": {
    "schema": "micromax.mxtest.source.v1",
    "algorithm": "sha256",
    "digest": "...",
    "files": [
      {"path": "src/micromax/vm.py", "size": 1234, "sha256": "..."}
    ]
  }
}
```

The covered surfaces are the repo files that validation commonly depends on: top-level project/config notes plus `docs/`, `examples/`, `plugins/`, `portability/`, `scripts/`, `src/`, `tests/`, and `tools/`. Generated and noisy surfaces such as `.artifacts/`, caches, build/dist outputs, zip files, `__pycache__`, and `*.egg-info` metadata are excluded.

## Resume behavior

`tools/mxtest.py --run-chunks N --resume --json MANIFEST` now requires the previous manifest's top-level `source_digest` to match the current source digest before any passed chunk can be skipped. If the previous manifest is old, missing the digest, or from a different source tree, mxtest reruns the chunks instead of trusting stale evidence.

The node-id digest still matters. Resume now requires both:

- matching source digest at the aggregate manifest level
- matching per-chunk index/total, strategy, selected count, first/last node ids, and ordered node-id digest

## Diff and verification

`--diff-manifests OLD NEW` now compares `source_digest` and, when both manifests include embedded source manifests, reports path-level added/removed/changed source files. This makes a collection/duration drift easier to explain: the diff can say not only that a digest changed, but also which source files caused the change.

`--verify-manifest MANIFEST` also checks the internal consistency of any embedded source manifest: file count, total bytes, manifest digest, and top-level `source_digest` must agree with the manifest's file rows.

## Boundary

Rev753 does not claim cryptographic supply-chain security. The source manifest is an in-repo validation guard, not a signed provenance artifact. It protects the handoff workflow from an easy mistake: resuming old test evidence after source content changes without noticing.

Future work can add stronger source policy, such as optional current-tree verification, source-digest allowlists for multi-machine handoffs, or splitting the manifest into test/source/doc subsets when the all-file digest is too coarse.
