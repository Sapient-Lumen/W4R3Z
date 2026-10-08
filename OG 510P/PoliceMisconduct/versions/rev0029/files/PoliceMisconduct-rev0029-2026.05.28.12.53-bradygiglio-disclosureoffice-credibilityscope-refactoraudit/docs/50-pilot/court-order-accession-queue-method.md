# Court/order accession queue method

Rev0006 does not yet download or summarize court orders. It creates an accession queue.

Each queue row identifies:

- expected artifact type;
- expected date if known;
- matter ID and source row;
- known source signals that mention the artifact;
- locator sources;
- claim power after accession;
- privacy and summary gates.

The queue is deliberately not a docket. It is a retrieval and proof-plan surface.

## Why this matters

A consent decree termination order, a motion to terminate, a partial termination order, a sustainment plan, and a closing letter are not interchangeable. The cube must know which kind of artifact it has before it can state what changed.
