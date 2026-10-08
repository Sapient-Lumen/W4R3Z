# 913 — Offline cache receipts, DNS preflight, and root-entrypoint drift

**Track:** Shared / Release evidence / Source authority / Operator tooling

Revision `v875` focuses on the source-byte work most likely to stall: converting the acquisition queue into receipts when this cloudtainer cannot resolve public hostnames.

## What changed

`rev0874` made the remaining pinned-source work finite by assigning every pinned row a stable `local_filename` and queueing the `105` pinned rows that still lacked receipts. The next attempted step was to execute that queue. The cloudtainer failed before byte transfer: DNS resolution failed for public hosts, including the RFC Editor and the first high-impact queue hosts.

This revision does not fake source-byte receipts. It adds the missing offline path instead:

- `scripts/source_byte_receipt_from_cache.py` verifies an already-populated external cache file against the lockfile sha256 and writes a receipt only after the digest matches.
- `tools/source_byte_receipt_pack.py` now records explicit receipt observation types.
- Existing receipts are marked `network_fetch`.
- Future no-network receipts must be marked `operator_cache_file`, must carry `fetch_status=not_applicable_cache_file`, and must set `cache_file_sha256_matched=true`.
- `scripts/check_source_byte_acquisition_queue.py` smoke-tests the new cache receipt helper in `--print-plan` mode, proving source-id resolution without network I/O.

The source-byte receipt count remains `13`. That is intentional. The session did not obtain new third-party bytes, so the archive should not claim new byte observations.

## DNS preflight evidence

`artifacts/reports/source-byte-dns-preflight-rev0875.json` records a host-level preflight for the next `20` receipt-missing queue rows. In this cloudtainer, all `8` unique hosts in that selected batch failed DNS resolution.

That report is environment evidence, not a portable release gate. It exists to prevent the next maintainer from mistaking the stalled receipt count for completed review, and to make the immediate blocker visible: source bytes need to be supplied through an external cache or through a network-enabled environment.

## Root-entrypoint drift refactor

The audit found a concrete drift bug in `rev0874`: `VERSION` and the top `CHANGELOG.md` entry said `v874`, but `README.md` and `ARCHIVE_INDEX.md` still started with `v873`. That kind of mismatch is small but dangerous because the root entrypoints are what reviewers open first.

`scripts/check_version_consistency.py` now checks `README.md` and `ARCHIVE_INDEX.md` near the top, in addition to `VERSION`, `CHANGELOG.md`, and `docs/START_HERE.md`. A future revision bump should fail fast if the root entrypoints lag again.

## Operator path

Network-enabled path:

`python3 scripts/fetch_source_sha256.py --source-id <source_id> --cache-dir /path/to/source-cache --write-receipt`

No-network external-cache path:

`python3 scripts/source_byte_receipt_from_cache.py --source-id <source_id> --cache-dir /path/to/source-cache --write-receipt`

The no-network path expects `/path/to/source-cache/<local_filename>` to already exist. It never fetches the network, never bundles third-party bytes, and fails unless the file hash equals the lockfile sha256.

## Boundary

This revision still does not establish current voter instruction, legal advice, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## Size-discipline refactor

Several release-generated JSON packs now use compact deterministic JSON (`sort_keys=True`, stable separators) for checked artifacts rather than pretty-printing large machine-readable matrices. This is intentionally a generator-level refactor, not a post-gate mutation: byte-comparison gates should regenerate the same compact JSON that ships in the archive. The object semantics are unchanged; the saved bytes make room for source-byte acquisition mechanics without deleting evidence.
