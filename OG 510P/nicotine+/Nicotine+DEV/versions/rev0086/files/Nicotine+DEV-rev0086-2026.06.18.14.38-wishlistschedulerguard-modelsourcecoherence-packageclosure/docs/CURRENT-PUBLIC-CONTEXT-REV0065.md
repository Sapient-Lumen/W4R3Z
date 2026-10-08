# Current public context — rev0065

Refreshed during rev0065 to keep the public/private boundary current.

Observed public context:

```text
Nicotine+ NEWS: Version 3.3.11 Release Candidate 1 remains listed.
3.3.11 RC1 corrections include broad items for uncompressed network-message size limits, upload-spoofing prevention, username identity fixes, distributed-search fixes, and empty-room search crash behavior.
GitHub 3.3.11 milestone: observed open, 97% complete, one open item.
Open item: PR #3781, Implement safe path joining to prevent path traversal.
PR #3781 text describes safe_path_join() removing illegal/path-traversal components and keeping the final path under the base path.
```

Boundary retained: PR #3781 and historical PR #3723 remain public-watch/public-overlap context only. rev0065 does not open a private path traversal row and does not retire any of the seven strict/front packets solely on broad release-note wording.

References recorded for human reviewers:

```text
https://nicotine-plus.org/NEWS.html
https://github.com/nicotine-plus/nicotine-plus/milestone/15
https://github.com/nicotine-plus/nicotine-plus/pull/3781
```
