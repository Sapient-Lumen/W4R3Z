# Rev1020 audit

Rev1020 replaces whole-catalog and whole-history one-file rename planning with exact startup-attested content indexes and bounded two-row cutpoints. Catalog publication now streams canonical rows with O(1) retained row memory. Actual rename publication deliberately retains one O(N-visible) streaming integrity fence, and catalog mutation deliberately retains one O(N) canonical digest pass.

The adjacent audit corrected the v5-to-v6 intermediate catalog migration, preserved bounded two-head conflict adoption, repaired inherited lexical oracles after schema v9, and excluded a divergent hidden prototype and all interrupted or stale build trees.

This is regular-file scale work, not directory/subtree move semantics, dense million-file throughput proof, Android support, conflict UX, retention collection, ENOSPC recovery, or live public Tor/I2P qualification.
