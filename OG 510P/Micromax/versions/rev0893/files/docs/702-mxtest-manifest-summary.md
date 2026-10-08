# Rev758 — mxtest manifest summary

Rev752 through rev757 made aggregate mxtest manifests increasingly trustworthy: they can carry duration history, diff against other manifests, recommend future chunk plans, attest source, attest environment, gate resume skips, and answer whether an old manifest is still current. One handoff gap remained: a human still had to scan a large JSON file or run several narrow commands just to answer "what happened in this validation run?"

Rev758 adds the compact summary path:

```bash
python tools/mxtest.py --manifest-summary .artifacts/mxtest-all.json
```

The command does not collect tests and does not run pytest. It loads an existing mxtest JSON object and prints the high-signal fields:

```text
mxtest manifest summary:
status: passed complete=true returncode=0
selection: collected=1518 selected=1518 chunks=8 strategy=segment
duration: 123.456s
chunk statuses: passed=8 failed=0 timed_out=0 partial=0 not_run=0
source: 123456789abc files=842 bytes=1234567
environment: abcdef123456 python=3.11.9 pytest=8.2.2
slowest chunks (top 5):
- chunk 4/8: 28.500s status=passed selected=184
slowest files (top 5):
- chunk 4/8 tests/test_editor_docs_navigation.py: 17.200s status=passed selected=91
```

Use `--summary-limit N` to control how many slowest chunk and file rows appear. Use `--json PATH` when a handoff wants the same summary in plain data:

```bash
python tools/mxtest.py --manifest-summary .artifacts/mxtest-all.json --summary-limit 10 --json .artifacts/mxtest-summary.json
```

The JSON payload includes:

- `status`, `complete`, `returncode`, and `duration_seconds`
- `collected`, `selected`, `run_chunks`, and `strategy`
- `chunk_status_counts`
- full and short source/environment digests
- source file count and total bytes
- Python and pytest versions from the embedded environment manifest
- `slowest_chunks`
- `slowest_files`
- `manifest_issues` when the input is a `run-chunks` aggregate with internal consistency problems

## Makefile helper

```bash
make test-manifest-summary
```

The helper reads `.artifacts/mxtest-all.json`, matching the default all-chunks output path.

## Audit/refactor note

Rev758 also extracts a shared `emit_lines_and_json(...)` helper for no-run mxtest commands that produce human lines plus optional JSON. The current-source verifier, current-environment verifier, bundled current verifier, manifest diff, chunk recommendation, and manifest summary now use the same emission path. This is intentionally small, but it matters: no-run audit commands should not each reinvent JSON-writing and line-printing behavior.

## Trust boundary

The summary command is not a replacement for `--verify-manifest` or `--verify-current`. It is a readable digest. It may surface embedded `manifest_issues` for aggregate manifests, but it does not rerun stale chunks, recalculate current source applicability, or prove host stability. Use it first to understand the artifact; use the verifier commands to decide whether to trust or resume it.
