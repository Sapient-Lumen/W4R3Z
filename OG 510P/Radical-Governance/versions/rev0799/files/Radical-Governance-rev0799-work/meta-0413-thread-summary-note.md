# Meta 0413 — thread summary index note

This revision adds `THREAD_SUMMARY.json`, a very small machine-readable companion to `THREADS.md`.

Purpose:

- expose note-count density by inferred tag,
- identify the latest note per tag,
- make it easier to spot where the continuation bundle is getting deep or still thin,
- and support later merges or comparisons without scraping prose crosswalks.

The summary is intentionally compact. It does not replace `ARCHIVE_INDEX.json`, `THREADS.md`, or `RELEASES.json`; it gives the bundle a quick “where is the archive concentrating?” view that can be used by humans or simple tooling.
