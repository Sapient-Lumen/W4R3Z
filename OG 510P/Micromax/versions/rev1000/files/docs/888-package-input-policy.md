# Package input policy (rev0930)

Rev0930 closes the release-hygiene gap left after the archive verifier: a handoff
zip can now explain the package/dependency inputs that produced it.  This does
not pretend to be a lock file or hosted attestation.  It makes the current
policy executable and fail-closed when the project drifts into a riskier shape.

## Why this was the riskiest next release slice

Rev0929 made archive contents self-verifying, but the artifact still could not
say whether its Python package inputs were locked, intentionally unlocked, or
silently drifting.  Current Python packaging guidance now has a standardized
`pylock.toml` format for reproducible installs, and SLSA provenance frames build
inputs/fetched artifacts as materials to record.  Micromax does not yet need a
full lock because the package has no runtime dependencies; it does need a
machine check that this remains true and that dev/tool inputs do not split across
files unnoticed.

## What changed

- `pyproject.toml` now carries an explicit local release policy:
  - `dependency_policy = "unlocked-dev-only"`
  - `package_version_policy = "archive-revision-independent"`
- `tools/mxrelease.py --package-inputs` emits and verifies a compact package
  input report.
- `make release-inputs` exposes that report as a normal handoff command.
- `tools/mkrevzip.py` embeds the package-input report into
  `MICROMAX-CONTEXT.json` inside every handoff archive.
- `tools/mxaudit.py --check` hard-checks `package_input_policy_present` so this
  does not decay into a forgotten convention.

## Executable policy

`mxrelease.package_input_report()` currently accepts the no-lock stance only
when all of the following remain true:

1. `[tool.micromax.release].dependency_policy` is exactly
   `unlocked-dev-only`.
2. `[tool.micromax.release].package_version_policy` is exactly
   `archive-revision-independent`.
3. No recognized lock file (`pylock.toml`, `uv.lock`, `poetry.lock`,
   `Pipfile.lock`, or `requirements.lock`) is present.
4. `[project].dependencies` is absent/empty, so the shipped package has no
   runtime dependency graph to resolve.
5. `requirements-dev.txt` mirrors `[project.optional-dependencies].dev`.
6. Remote pre-commit hooks use non-floating `rev:` values rather than
   `main`, `master`, `HEAD`, `latest`, or a variable/template.

If a runtime dependency appears, this check should fail until the project moves
to a lock/pinned input policy.  If a lock file appears, this check should fail
until the release policy is deliberately updated to consume it.

## Audit/refactor

This is deliberately a release-tool refactor, not a new registry.  The package
input rules live beside release-suite evidence in `mxrelease`, the archive
handoff consumes the same report through `mkrevzip.package_input_snapshot()`, and
`mxaudit` only checks the executable seam and focused regressions.

## Validation

Completed under the cloudtainer:

```bash
PYTHONPATH=src python tools/mxrelease.py --package-inputs
PYTHONPATH=src python tools/mxaudit.py --check --limit 3
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxrelease.py
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxaudit.py
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mkrevzip.py::test_mkrevzip_embeds_package_input_policy_report
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mkrevzip.py::test_mkrevzip_verify_archive_cli_json
```

The full `tests/test_mkrevzip.py` selector printed `14 passed, 1 warning` in
one run, but the outer tool wrapper did not return cleanly afterward; the split
selectors above are the conservative evidence for this revision.

## Remaining risk

- This is not a dependency lock.  It is an executable no-runtime-deps/no-lock
  policy.
- The package version remains independent from handoff `rev####` archives by
  explicit policy; that is acceptable while archives are session handoffs, but a
  published package lane should revisit it.
- There is still no CI workflow, signature, SBOM, or SLSA attestation.
- The next runtime step should return to a concrete owner/lifetime seam
  (prompt history, active interactions, macros, or clipboard) rather than
  expanding release ceremony.
