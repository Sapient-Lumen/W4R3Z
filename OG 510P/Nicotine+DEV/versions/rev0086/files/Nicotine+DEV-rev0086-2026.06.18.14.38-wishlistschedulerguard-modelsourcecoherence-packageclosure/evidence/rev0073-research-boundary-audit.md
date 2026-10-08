# rev0073 research-boundary and provenance audit note

`tools/audit_rev0073_research_boundary.py` gates the six current landing surfaces, inventories historical readiness language, and groups U-123 files by exact hash and semantic path role.

Final corrected result:

```text
status: pass
historical files with readiness terms: 321
inventory rows: 329
historical exact U-123 duplicate groups: 2
rows in duplicate groups: 5
safe U-123 deletions: 0
write idempotence: pass
```

The original construction version scanned its own generated inventory and summary on later runs, corrupting its totals. Rev0073 now excludes only those generated outputs and its regex-bearing auditor source, then recomputes after writing and fails on any difference. Two consecutive write runs produced identical output hashes.

The active rev0073 U-123 artifacts are unique after the shared-harness refactor. The remaining exact groups belong to the byte-preserved rev0072 archive and older revision-scoped handoffs; they remain because their paths carry provenance.
