# mxtest current-source verification (rev754)

Rev753 embedded a source manifest in mxtest plan/run JSON and used the top-level `source_digest` to stop stale `--resume` skips. Rev754 closes the next handoff gap: a manifest could be internally consistent, but there was no direct no-run command for asking whether that manifest still described the current checkout.

## Command

Use:

```bash
python tools/mxtest.py --verify-current-source .artifacts/mxtest-all.json
```

This reads the manifest, computes the current tree's `micromax.mxtest.source.v1` source manifest, and compares the embedded manifest source with the files on disk. It does **not** collect pytest node ids and does **not** run tests.

The optional JSON form is:

```bash
python tools/mxtest.py --verify-current-source .artifacts/mxtest-all.json --json .artifacts/current-source.json
```

## Exit codes

- `0`: the manifest's embedded source digest matches the current source tree
- `1`: the manifest is structurally valid, but the current source tree has drifted
- `2`: the manifest is malformed, missing source attestation, or has an internally inconsistent source manifest

## Reported evidence

The text output includes the manifest digest prefix, the current digest prefix, and whether they match. When source file rows are available, drift reports path-level added, removed, and changed files, reusing the same source-diff machinery as `--diff-manifests`.

The JSON payload includes:

```json
{
  "mode": "verify-current-source",
  "matches_current_source": false,
  "source_digest": "...",
  "current_source_digest": "...",
  "source_differences": {
    "added": ["..."],
    "removed": ["..."],
    "changed": ["..."]
  },
  "issues": []
}
```

## Makefile helper

```bash
make test-verify-current-source
```

The helper checks `.artifacts/mxtest-all.json`, matching the default aggregate manifest used by `make test-all-chunks`.

## Boundary

Plain `--verify-manifest` remains an offline consistency check for the manifest itself. It can be run on an artifact from another machine without reading the local source tree. `--verify-current-source` is intentionally stronger and more local: it reads the current checkout to decide whether an old validation claim still applies here.

This still is not signed provenance or environment attestation. It answers one narrow trust question: "does this manifest's source evidence match the files I have now?"
