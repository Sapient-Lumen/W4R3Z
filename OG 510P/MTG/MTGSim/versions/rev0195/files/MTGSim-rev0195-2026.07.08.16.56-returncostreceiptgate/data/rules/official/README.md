# rev0170 official-rules metadata note

This datacube still does not bundle official Wizards rules text. The local metadata source remains pinned to the packaged 2026-04-17 manifest while the session observed a current public rules effective date of 2026-06-19. rev0170 changes replay artifact code, not the official-rules source cache.

---

# Official rules cache

The official rules documents are not bundled here. The manifest records official URLs and effective dates. Run:

```bash
python3 tools/fetch_official_rules.py --out data/rules/official/cache
```

That creates a local cache and `cache_index.json` with sizes, content types, hashes, and server metadata. Keep the cache private unless you have reviewed redistribution rights.
