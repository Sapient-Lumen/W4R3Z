# Current-tool discovery refactor — rev0082

Two current validators still encoded rev0081 conclusions in Python even though their surrounding contracts were advertised as revision-neutral.

## Source-contract audit defect

The source-identity audit constructed the expected probe filename as:

```text
probe_<revision>_search_rekey.py
```

Renaming the current research probe to `probe_rev0082_search_consumers.py` made the source contract fail despite a valid revision contract and valid source use. The validator now discovers source-consuming tools from `data/current_revision_contract.json` and selects those that import `source_bundle_locator`, rather than guessing a research topic from the revision number.

## Navigation audit defect

The navigation audit hard-coded `SEARCH-AGAIN-EPOCH-01` as the only valid primary packet. Splitting the packet into `01A` and `01B` therefore failed even though the machine ledger and packet contract agreed.

The audit now validates that `primary_packet_id` is well-formed and exists in `data/current_packet_dispositions.json`. It no longer owns a competing packet list.

## Principle

A validator should enforce structure and cross-authority coherence. It should not restate the current topic, filename, packet ID, or disposition in code. Those values belong in current contracts, where mutation controls and package checks can see them.
