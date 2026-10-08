# rev0071 cloudtainer waste / source-alias audit

Run from the cube root:

```bash
python tools/probe_rev0071_cloudtainer_waste.py --source-zip /path/to/Nicotine-source.zip --validate-existing
```

For this session, `/mnt/data/Nicotine-source(2).zip` was used and matched the expected archived-source SHA256:

```text
feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
```

Expected result:

```text
status: pass
source_zip_status: pass
ranked_audit_queue_share_pct: high/dominant
exact_duplicate_wasted_bytes: nonzero, reviewable
```

This is not a Nicotine+ code patch. It is a cube hygiene correction that makes future compaction and current-source prioritization explicit.
