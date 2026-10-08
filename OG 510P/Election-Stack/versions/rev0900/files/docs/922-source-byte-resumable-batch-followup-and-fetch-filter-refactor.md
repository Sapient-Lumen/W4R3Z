# 922. Source-byte resumable batch follow-up and fetch-filter refactor

**Track:** Shared / source-byte completion / operator-resume tooling

**Revision:** `v884`  
**Status:** synthetic-release only; no live-pilot, legal, certification, source-currentness, source-byte cache completeness, or public-voter-instruction claim.

The highest completion risk remains unchanged: `118` pinned external sources exist, `13` have valid source-byte receipts, and `105` still lack receipts. The risk is not that the archive lacks prose about the gap; the risk is that a network-capable operator can start batch `01`, hit one bad host or partial success, and then lose the exact next move.

This revision adds resumability and routing without promoting any source to current authority.

## What changed

`v884` keeps the current first incomplete handoff at:

- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0884-batch01.sha256`

It adds a current fetch plan and follow-up handoff:

- `artifacts/reports/source-byte-batch-fetch-plan-rev0884.json`
- `artifacts/reports/source-byte-batch-followup-rev0884.json`
- `artifacts/source_byte_cache_intake/followups/source-byte-cache-followup-rev0884-batch01-unresolved.sha256`

Because the shipped plan is intentionally no-network/plan-only, the current follow-up `.sha256` file is identical to batch `01`: all `20` rows remain unresolved. That is expected. The value is the executable path for a real partial run.

## Operator execution shape

Start with the current batch fetcher on a network-capable host with an external cache directory:

```sh
python3 scripts/fetch_source_byte_batch.py \
  --batch-file artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0884-batch01.sha256 \
  --cache-dir /path/to/external-source-cache \
  --write-receipts \
  --write-report
```

If one source is blocking progress, route around it without editing the batch file:

```sh
python3 scripts/fetch_source_byte_batch.py \
  --batch-file artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0884-batch01.sha256 \
  --cache-dir /path/to/external-source-cache \
  --write-receipts \
  --skip-source-ids SOURCE_ID_TO_SKIP \
  --write-report
```

After any partial attempt, build the next strict unresolved-row handoff:

```sh
python3 scripts/build_source_byte_batch_followup.py \
  --attempt-report artifacts/reports/source-byte-batch-fetch-plan-rev0884.json \
  --write
```

The follow-up builder separates two cases that were previously easy to blur:

1. rows whose bytes still need fetch/cache verification; and
2. rows whose bytes matched but still need a receipt write.

It performs no network I/O, writes no receipts, and never vendors third-party bytes into the release archive.

## Audit/refactor result

The audited surface was the source-byte operator path. The brittle part was not the lockfile itself; it was the lack of a safe, deterministic follow-up after partial execution. `--limit` alone was not enough because it only helped with the front of the batch. `--only-source-ids` and `--skip-source-ids` now let an operator continue around one failed source, and the follow-up builder converts actual attempt status back into a governed `.sha256` handoff.

New and modified gates:

- `scripts/check_source_byte_batch_fetcher.py` now proves strict source-id include/skip behavior as well as no-network plan/cache smoke coverage.
- `scripts/check_source_byte_batch_followup.py` proves the current plan-only follow-up is current, and a fixture partial attempt yields exactly one unresolved fetch row plus one receipt-only action.
- `docs/162-release-and-ci-evidence-pipeline.md` now lists the follow-up gate so the resumability surface cannot become undocumented drift.

## Remaining highest-risk work

1. Run batch `01` on a network-capable host and import only exact-match receipts.
2. Run the follow-up builder after the first real attempt; use the unresolved `.sha256` file rather than editing batch files by hand.
3. Repeat batches in order until the receipt gap is closed or each remaining source has an explicit acquisition failure reason.
4. Review freshness/currentness separately; SHA-256 receipts prove observed bytes, not current law, current voter instruction, or jurisdictional authority.

Machine-readable reports:

- `artifacts/reports/source-byte-batch-followup-rev0884.json`
- `artifacts/reports/risk-priority-forward-motion-rev0884.json`
