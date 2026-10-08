# mxtest environment attestation (rev755)

Rev753 and rev754 made source truth checkable: manifests now embed source digests, resume skips are source-gated, and `--verify-current-source` can decide whether a manifest still describes the checkout in front of the user. Rev755 closes the adjacent handoff gap: a source-stable manifest can still be misleading when it was produced by a different Python, pytest, platform, or test-environment setting.

## Manifest fields

Every mxtest plan/run JSON now embeds a small `micromax.mxtest.environment.v1` manifest:

```json
{
  "environment_digest": "...",
  "environment_manifest": {
    "schema": "micromax.mxtest.environment.v1",
    "algorithm": "sha256-json",
    "python": {
      "implementation": "CPython",
      "version": "3.11.8",
      "version_info": [3, 11, 8, "final", 0],
      "executable": "/path/to/python"
    },
    "platform": {
      "system": "Linux",
      "release": "...",
      "version": "...",
      "machine": "x86_64",
      "processor": "..."
    },
    "pytest": {
      "version": "...",
      "disable_plugin_autoload": "1"
    },
    "packages": [
      {"name": "pytest", "version": "..."}
    ],
    "env": {
      "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"
    },
    "digest": "..."
  }
}
```

The digest is computed over the manifest content excluding the digest field itself. The manifest is intentionally lightweight. It is not a dependency lockfile, a signed provenance statement, or a full environment dump. It records the host facts most likely to explain why two source-identical test runs disagree.

## Current-environment verification

Use:

```bash
python tools/mxtest.py --verify-current-environment .artifacts/mxtest-all.json
```

This command reads the manifest, computes the current host's environment manifest, and compares the two environment digests. It does **not** collect pytest node ids and does **not** run tests.

The optional JSON form is:

```bash
python tools/mxtest.py --verify-current-environment .artifacts/mxtest-all.json --json .artifacts/current-environment.json
```

## Exit codes

- `0`: the manifest's embedded environment digest matches this host
- `1`: the manifest is structurally valid, but environment drift was detected
- `2`: the manifest is malformed, missing environment evidence, or has an internally inconsistent environment manifest

## Diff and verify integration

`--verify-manifest` now checks embedded environment-manifest consistency when the fields are present. Backward compatibility is preserved: older manifests without environment evidence are not rejected by plain offline verification.

`--diff-manifests OLD NEW` now compares `environment_digest` and reports field-level added/removed/changed environment facts. This gives handoffs a no-run way to separate source drift from host drift.

## Makefile helper

```bash
make test-verify-current-environment
```

The helper checks `.artifacts/mxtest-all.json`, matching the default aggregate manifest used by `make test-all-chunks`.

## Boundary

Rev755 introduced environment attestation as evidence. Rev756 makes that evidence part of resume safety: `--run-chunks --resume` now skips previous passed chunks only when the prior and current `environment_digest` match as well as the source and chunk evidence. This document remains the manifest-format reference; see `docs/700-mxtest-resume-environment-gate.md` for the enforcement boundary.
