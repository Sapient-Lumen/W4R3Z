# Rev757 — mxtest current-manifest audit

Rev754 added a no-run current-source audit. Rev755 added a no-run current-environment audit. Rev756 made resume skip decisions require both source and environment stability. One handoff gap remained: a user still had to run three separate commands to answer the practical question, "is this aggregate validation manifest still safe to treat as current evidence here?"

Rev757 adds the bundled audit:

```bash
python tools/mxtest.py --verify-current .artifacts/mxtest-all.json
```

The command does not collect or run pytest. It loads the manifest once, then checks:

1. aggregate manifest integrity through the existing `--verify-manifest` path;
2. embedded source evidence against the current checkout; and
3. embedded environment evidence against the current host.

The human output is intentionally small:

```text
mxtest current-manifest verification:
manifest: ok
source: ok
environment: ok
resume-safe: true
```

When drift is present, it summarizes the same path/field counts used by the narrower verifiers and returns a non-zero code. With `--json`, the command writes a compact handoff payload:

```json
{
  "mode": "verify-current",
  "resume_safe": true,
  "manifest_ok": true,
  "source_ok": true,
  "environment_ok": true,
  "source_digest": "...",
  "current_source_digest": "...",
  "environment_digest": "...",
  "current_environment_digest": "...",
  "issues": []
}
```

Exit codes follow the same trust vocabulary as the narrower checks:

- `0`: the aggregate manifest is internally valid, passed, source-current, and environment-current;
- `1`: the manifest is structurally readable, but it is not resume-safe because status/source/environment does not line up; and
- `2`: the manifest or its embedded evidence is malformed or missing required structure.

`make test-verify-current` exposes the default project path:

```bash
make test-verify-current
```

This does not replace the narrower commands. It is the handoff preflight: use it before trusting a previous all-chunks artifact; use the narrower commands when you need to investigate only source drift or only host drift.
