# 912 — Source-byte acquisition queue and cache-basename firewall

**Track:** Shared

Revision `v874` cuts the next source-byte reproducibility risk without adding a bulky third-party cache to the release archive.

The prior receipt lane proved selected pinned source observations. The remaining problem was operational: most pinned rows still required a maintainer to inspect `evidence/lock/external-sources.toml`, infer a safe local filename, manually run a fetch, and remember how to emit a receipt. That made the riskiest unfinished work easy to postpone and easy to do inconsistently.

## What changed

Every pinned lockfile row now has a deterministic `local_filename`. `scripts/check_external_sources_lockfile.py` treats that field as required for pinned rows, not optional. This gives `scripts/verify_external_sources_lock.py` a stable lookup target for all `118` pinned sources.

`tools/source_byte_acquisition_queue.py` now builds `artifacts/reports/source-byte-acquisition-queue.json`. The queue joins the external-source lockfile with the source-byte receipt report and records which pinned rows already have receipts and which rows remain queued for operator fetch work.

`artifacts/reports/source-byte-acquisition-queue.json` currently records:

- `118` pinned sources.
- `118` pinned sources with stable local filenames.
- `13` receipt-present rows.
- `105` receipt-missing rows.
- `71` high-impact unreceipted rows.
- `30` protocol unreceipted rows.
- `4` background unreceipted rows.

The high-impact batch is intentionally first because it covers voter-information, EAC/NIST/CISA/CDF, accessibility/language, audit/RLA, AI/synthetic-media, and related official-source rows. Protocol rows matter, but they are less likely to be the blocker for a local adopter capture or current-source refresh.

## Operator path

`python3 scripts/fetch_source_sha256.py --source-id <source_id> --cache-dir /path/to/source-cache --write-receipt`

The helper now resolves source ID, URL, expected sha256, and local cache filename from the lockfile. `--print-plan` performs no network I/O and is smoke-tested by `scripts/check_source_byte_acquisition_queue.py`; actual fetches remain operator-initiated and external to the release archive.

The cache boundary remains explicit: fetched third-party bytes must stay outside release ZIPs. A local `evidence/cache/` or external source-cache directory can be verified by `scripts/verify_external_sources_lock.py`, but it remains excluded from governed release payloads.

## New gate

`/scripts/check_source_byte_acquisition_queue.py` fails if:

- The acquisition queue report is stale.
- A pinned row lacks `local_filename`.
- Local cache basenames collide.
- Receipt-present/missing counts disagree with the receipt report.
- The next fetch batch is empty while receipt work remains.
- Queue rows lose the non-instruction/non-legal-advice boundary.
- `scripts/fetch_source_sha256.py --source-id ... --print-plan` cannot resolve a queued source without network I/O.

## Boundary

This revision still does not establish current voter instruction, legal advice, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.
