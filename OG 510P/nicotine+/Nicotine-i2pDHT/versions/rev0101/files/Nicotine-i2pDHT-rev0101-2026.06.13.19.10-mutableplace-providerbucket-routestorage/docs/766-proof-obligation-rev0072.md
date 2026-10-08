# Proof obligations rev0072

The current proof obligations are:

1. Summary receipt must not authorize archive or prune by itself.
2. Import archive must preserve contradiction, handoff, import, and summary-lineage memory.
3. Lineage prune must reject raw leaks, digest drift, boundary drift, hard-negative pressure, and contradiction dropping.
4. Fold/audit surfaces must keep rev0072 visible without deleting rev0071 predecessor history.
