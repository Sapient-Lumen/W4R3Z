# Archive Invariants

These are the archive truths that should survive future refactors.
They are narrower than the full policy docs and more semantic than a raw schema check.
Use them when you need to remember **what must not quietly drift**.

## Current invariants

1. **INV-0001 — Default no-publication posture**  
   Absent a new explicit written decision, the archive defaults to hold / no publication.

2. **INV-0002 — Legacy Mathematics links remain canonical**  
   The five Mathematics-era links remain the current public citation heads until a later explicit decision says otherwise.

3. **INV-0003 — Frozen in repo is not automatically public**  
   A frozen entry under `published/` is not automatically a current public citation head.

4. **INV-0004 — Canonical published artifact is TeX**  
   The canonical published freeze is the `.tex` source.

5. **INV-0005 — Compact surfaces must agree or fail closed**  
   If the compact state surfaces disagree, default to no publication until repaired.

6. **INV-0006 — Shipped archive is source-first and transient-pruned**  
   The shipped bundle should prefer source and control surfaces over compile byproducts and caches.

7. **INV-0007 — Revision identity is singular**  
   `VERSION`, `RELEASE_MANIFEST.json`, `REVISION_RECEIPT.json`, `ARCHIVE_INDEX.json`, and `release_queue/QUEUE_INDEX.json` should all point at the same shipped revision.

Machine-readable companion: `publishing/archive_invariants.json`.
Verification report: `reports/archive_invariants.json`.
