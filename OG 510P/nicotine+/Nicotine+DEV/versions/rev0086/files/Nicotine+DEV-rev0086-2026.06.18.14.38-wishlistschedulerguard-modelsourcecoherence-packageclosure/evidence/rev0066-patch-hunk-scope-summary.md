# rev0066 patch hunk-scope summary

rev0066 validates the exported rev0059 split strict/front patches at hunk granularity against the uploaded archived source bundle.

```text
source bundle SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
bundle patches parsed: 12
file-scope rows: 15/15 pass
hunk preimage rows: 41/41 pass
marker contract rows: 30/30 pass
negative controls: 4/4 pass
package hygiene rows: 3/3 pass
```

The gate reads source bytes directly from `/mnt/data/Nicotine-source(1).zip`, parses each unified diff, validates that only expected files are touched, checks every context/removal line against the original source, rebuilds the patched file in memory, and compares the resulting hash to the inherited rev0059 patched-file ledger.
