# Archive and evidence tiering — rev0072

## What actually caused the size spike

rev0071 contains 986,860,303 uncompressed member bytes and its linked ZIP is 987,560,883 bytes. Every one of its 2,067 files used ZIP's store-only method. rev0070 contained almost the same raw payload—986,557,824 bytes—but explicit deflation reduced its member payload to 44,858,471 bytes.

That is a packaging regression, not a 900 MiB increase in scientific evidence. Python's `zipfile.ZipFile` defaults to `ZIP_STORED` unless a compression method is supplied. rev0072 removes that ambient default from the release path.

## New release path

`src/muc5/archive_contract.py` and `scripts/build_linked_archive.py` now:

1. require a valid cube identity and a passing directory package contract;
2. write every file with explicit DEFLATE compression;
3. normalize archive timestamps and modes so identical input bytes rebuild identically;
4. reject path traversal, duplicate members, identity mismatches, CRC failures, and large store-only members;
5. enforce a configurable linked-archive budget, defaulting to 64 MiB.

The budget is a guardrail, not a scientific veto. A revision may deliberately raise it, but doing so becomes an explicit reviewed decision rather than an unnoticed consequence of a packaging default.

## Two-tier evidence model

The old process treated every textual mention of a raw filename as a reason to keep that file in the core forever. That mixed four very different relationships:

- a script that produces an output;
- a historical script that optionally reads a cache;
- an audit that only needs row count or hash metadata;
- a true current row-level consumer.

rev0072 keeps six current row-level dependencies in the core and moves the remaining 72 bulky records to a separate immutable sidecar. The sidecar is not a lossy summary. Every source byte is retained and checked against the pre-migration SHA-256.

The core catalog supplies row counts for inherited checks that only validated volume. This means the audit no longer forces hundreds of megabytes of transition tables into each revision merely to ask whether a historical run had 42,567 rows.

## Restoration and finalization

Cold evidence is restored by original path:

```bash
PYTHONPATH=. python scripts/materialize_evidence.py /path/to/evidence.zip
PYTHONPATH=. python scripts/materialize_evidence.py /path/to/evidence.zip data/rev0047_yield_online_cpp_transitions.csv
```

Materialization verifies the sidecar digest, member byte count, and member SHA-256. Finalization refuses to delete a materialized file if its digest differs from the catalog, preventing accidental loss of newly modified evidence.

## Process from now on

The default linked artifact should be the lean working cube. A cold evidence bundle changes only when new bulky evidence is admitted or old evidence is deliberately retired. New experiments should ship compact summaries and representative samples in core; row-level traces stay hot only while they are actively consumed. Once no current audit needs their rows, they move into the next append-only evidence layer.

This resembles established pointer/content-addressed patterns: Git LFS keeps text pointers in the repository while storing large content separately; OCI artifacts address immutable content by digest; and reproducible-build guidance recommends normalizing build timestamps instead of allowing wall-clock metadata to perturb outputs.

External references:

- https://docs.python.org/3/library/zipfile.html
- https://git-lfs.com/
- https://oras.land/docs/concepts/artifact/
- https://reproducible-builds.org/docs/source-date-epoch/
