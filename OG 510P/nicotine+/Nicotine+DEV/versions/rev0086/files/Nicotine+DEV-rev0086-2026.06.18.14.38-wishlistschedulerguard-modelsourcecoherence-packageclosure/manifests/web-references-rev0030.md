# rev0030 web references

- TinyTag on PyPI — https://pypi.org/project/tinytag/ — public upstream context: TinyTag is an audio metadata reader and supports WMA.
- TinyTag public source — https://github.com/tinytag/tinytag/blob/master/tinytag/tinytag.py — public source-shape adjacency for the WMA parser and `object_size - header_len` seek pattern; not a public bug report.
- GitHub Advisory Database GHSA-5v7r-6r5c-r473 / CVE-2026-31808 — https://github.com/advisories/GHSA-5v7r-6r5c-r473 — ASF parser zero-size/backwards-move infinite-loop class adjacency in a different package.
- Nicotine+ issue #3458 — https://github.com/nicotine-plus/nicotine-plus/issues/3458 — broad share-rescan slowdown report; not an exact WMA/ASF malformed-object-size report.
- Nicotine+ Release Notes — https://nicotine-plus.org/NEWS.html — broad 3.3.11 RC hardening context; not local media-parser scoped.
- GitHub issue search: `site:github.com/nicotine-plus/nicotine-plus tinytag WMA ASF object_size 24` — no direct exact issue/PR result found in captured searches.
- GitHub issue search: `site:github.com/tinytag/tinytag issues ASF WMA object_size header_len` — no direct exact issue/PR result found in captured searches.
