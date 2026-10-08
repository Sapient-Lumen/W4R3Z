# Defect: fresh-state campaigns mislabeled as inheritance probes

## Before

SQLite connection-affinity and owner-generation race campaigns forked first but
created their databases and relevant SQLite state only in the child. They paid
the copied-runtime risk without testing inherited authority.

## Correction

Both campaigns now enter versioned pinned self-exec workers: ten connection
scenarios and 32 owner-generation workers. True inherited-capability probes stay
on the inherited owner.
