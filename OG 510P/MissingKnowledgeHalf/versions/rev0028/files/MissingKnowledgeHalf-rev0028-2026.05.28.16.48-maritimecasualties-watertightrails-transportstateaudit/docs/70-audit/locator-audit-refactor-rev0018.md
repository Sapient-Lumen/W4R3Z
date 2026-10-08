# Locator audit/refactor — rev0018

Rev0018 includes a targeted refactor of the weak-locator detector.

Before: rev0017 reported 38 weak source locators and 44 weak claim refs.

After refined detection: rev0018 reports 32 weak source locators and 39 weak claim refs.

The source-locator reduction is mostly detector hygiene: the old audit matched the substring `search` inside words such as `research`. Those false positives are now separated in `LOCATOR-AUDIT-LEDGER.json`.

Remaining debt should be treated as real. The priority is to replace search/snippet locators in clinical/practice-lag and replication records with stable source locators or explicit unreachable-source statuses.
