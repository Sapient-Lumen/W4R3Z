# rev0057 current public context refresh

Observed on 2026-06-16 before packaging rev0057. This is current-public context only; it does not alter the seven strict/front private packets and does not convert the archived-source patch queue into live-current filing proof.

```text
Nicotine+ homepage: stable version still listed as 3.3.10; testers are pointed to the 3.3.11 release candidate.
NEWS: 3.3.11 Release Candidate 1 remains visible with broad correction wording around uncompressed network-message limits, upload spoofing, username identity, distributed search, and empty-room search behavior.
GitHub milestone 3.3.11: observed open, 97% complete, one open item.
PR #3781: public/open safe_path_join path-traversal work.
PR #3723: public/closed historical clean_path path-traversal context, superseded by #3781.
```

Boundary: PR #3781 and PR #3723 remain public-watch-only rows, and no path-traversal row is merged into the strict/front selected patch queue.
