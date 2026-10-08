# mxtest all-chunks resume manifest (rev751)

Rev751 closes the next test-runway gap after rev750.  The runner could plan balanced chunks and run any one chunk, but a full-suite handoff still required a human to run each chunk manually and mentally merge the evidence.  `tools/mxtest.py` can now run every planned chunk in one invocation and checkpoint one aggregate JSON manifest.

## New command

```bash
python tools/mxtest.py --run-chunks 8 --strategy segment --isolate-files --json .artifacts/mxtest-all.json
```

`make test-all-chunks` wraps the same cold-start default:

```bash
make test-all-chunks
make test-all-chunks CHUNKS=12
```

The command still collects once, builds the requested chunk plan, and then runs exact selected node ids.  It writes the aggregate manifest after every chunk when `--json` is provided, so an interrupted run leaves evidence instead of only terminal scrollback.

## Resume contract

```bash
python tools/mxtest.py --run-chunks 8 --strategy segment --isolate-files --resume --json .artifacts/mxtest-all.json
```

`--resume` only skips a previous chunk when all of these match:

- previous chunk status is `passed`
- chunk index and total match
- strategy matches
- selected count matches
- first and last node ids match
- ordered `nodeids_digest` matches

The digest is a SHA-256 over the exact ordered node-id selection with a delimiter between entries.  That makes resume safe against accidental reordering, changed filters, or changed collection output that happen to leave the same count behind.

A resumed chunk is preserved in `chunk_results` with:

```json
{
  "status": "passed",
  "resumed": true,
  "skipped": true,
  "skip_reason": "previous-passed-matching-chunk"
}
```

Failed, timed-out, missing, or mismatched chunks are rerun.

## Aggregate evidence

The all-chunks JSON includes:

- `mode: "run-chunks"`
- `run_chunks`
- full `chunks` counts
- `chunk_plan`
- `chunk_results`
- `chunk_status_counts`
- aggregate `status`
- aggregate `returncode`
- `complete`
- top-level and per-chunk `nodeids_digest`
- `execution_pytest_args` and `dropped_pytest_selectors`

This turns a full-suite claim into one inspectable artifact.  A handoff can now say exactly which chunks ran, which chunks were resumed, what node ids each chunk represented, and whether the manifest is complete.

## Fail-fast mode

`--fail-fast` stops after the first non-zero chunk and records the remaining chunks as `not_run` with `skip_reason: "fail-fast-after-earlier-nonzero"`.  The aggregate status becomes `partial`, and the process exits nonzero.  The default is to keep running so the manifest can collect as much failure evidence as possible.

## Trust boundary

The important rule is that resume is based on the selected node-id digest, not a vague file name or chunk number.  A passed chunk from an old manifest is only reused when it proves it corresponds to the current collection.  That keeps resumed validation from becoming another silent assumption.

## Manifest verification

Rev751 also adds a no-run verifier:

```bash
python tools/mxtest.py --verify-manifest .artifacts/mxtest-all.json
make test-verify-manifest
```

The verifier does not collect tests.  It loads the aggregate manifest, recomputes aggregate status and completeness from `chunk_results`, checks that every chunk has a valid index/total and a 64-character `nodeids_digest`, and returns:

- `0` for a structurally valid complete passed manifest
- `1` for a structurally valid manifest whose computed status is not passed
- `2` for malformed or self-contradictory manifests

This keeps the artifact useful after the run: a future handoff can verify the manifest before trusting its status line.
