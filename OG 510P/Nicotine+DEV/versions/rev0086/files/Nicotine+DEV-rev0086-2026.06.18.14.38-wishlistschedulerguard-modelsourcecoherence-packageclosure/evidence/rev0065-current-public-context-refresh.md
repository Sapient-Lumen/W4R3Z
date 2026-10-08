# Current public context refresh — rev0065

Refreshed during rev0065 using public web sources.

Observed:

- Nicotine+ NEWS still lists Version 3.3.11 Release Candidate 1.
- NEWS 3.3.11 RC1 corrections include broad language for uncompressed network-message limits, upload-spoofing prevention, username identity fixes, distributed-search fixes, and empty-room search behavior.
- GitHub milestone 3.3.11 was observed open, 97% complete, with one open item: PR #3781.
- PR #3781 remains public/open and describes `safe_path_join()` as removing illegal/path-traversal components and ensuring the final path remains under the base path.

Boundary:

- Public path traversal rows remain public-watch-only.
- Broad release-note language is not treated as exact overlap for the seven strict/front packets without current-source checkout/tarball classification.

Sources:

```text
https://nicotine-plus.org/NEWS.html
https://github.com/nicotine-plus/nicotine-plus/milestone/15
https://github.com/nicotine-plus/nicotine-plus/pull/3781
```
