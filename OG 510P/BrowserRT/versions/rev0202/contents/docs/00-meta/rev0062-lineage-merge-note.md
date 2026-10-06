# rev0062 lineage merge note

rev0062 merges the parallel rev0062 work lines observed in the cloudtainer:

- `BrowserRT-rev0062-2026.06.04.13.08-opfs-corrupt-block-repair-proof.zip`
- `BrowserRT-rev0062-2026.06.04.14.02-opfs-web-lock-tab-termination-proof.zip`
- `BrowserRT-rev0062-2026.06.04.14.05-opfs-web-lock-timeout-proof.zip`

The packaged head must move to `rev0062`, keep the Web Lock timeout/backstop runtime surface, keep the OPFS corrupt-block repair surface, keep the browser/CDP target helpers and lock-settled helpers, and prove the merged behavior in one browser slice rather than relying on registry text.

The audit goal is practical: prevent future turns from accidentally shipping two different archives with the same revision id or silently dropping one runtime branch while updating only the summary files.
