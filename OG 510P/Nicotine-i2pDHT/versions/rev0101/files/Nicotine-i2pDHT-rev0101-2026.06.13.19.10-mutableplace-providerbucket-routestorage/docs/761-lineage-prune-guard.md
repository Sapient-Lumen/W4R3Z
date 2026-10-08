# Lineage prune guard

Lineage pruning is not harmless cleanup.  It decides which wake-from-amnesia evidence survives after a redacted summary has been received and archived.

`lineageprune.py` requires summary receipt and import archive to agree at the same boundary before prune markers can pass.  The guard preserves:

```text
summary receipt
summary lineage
import archive
handoff import
contradiction memory
redacted summary memory
local archive marker
```

The important negative test is contradiction dropping.  A prune proposal that deletes the contradiction/fork/refutation thread quarantines even if the rest of the lineage looks settled.

lineage prune audit needle.
