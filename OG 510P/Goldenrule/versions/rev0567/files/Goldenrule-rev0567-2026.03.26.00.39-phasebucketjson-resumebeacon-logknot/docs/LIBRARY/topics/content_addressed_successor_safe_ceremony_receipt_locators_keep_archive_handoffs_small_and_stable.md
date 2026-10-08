# Content-addressed successor-safe ceremony receipt locators keep archive handoffs small and stable

The archive already has a compact, machine-checkable successor-safe ceremony receipt.
That solves the *shape* problem, but not yet the *citation* problem.
A future session can still keep re-copying the full receipt body into every derivative note, review packet, or process artifact.

Two source facts justify one tighter move:

- `RS-GR-509` says JSON Canonicalization Scheme (JCS) exists specifically to create an invariant, hashable JSON representation by constraining input to I-JSON and deterministically sorting properties.
- `RS-GR-510` says Named Information (`ni`) URIs exist to identify a digital object by its hash, separating the object's stable identity from whatever retrieval path later carries it.

That means the archive does not need to treat each successor-safe ceremony receipt as a prose blob that must be recopied to stay legible.
It can treat the receipt as a small structured object with one stable content address.

So the archive should ship a **content-addressed locator companion** beside each durable successor-safe ceremony receipt:

1. canonicalize the restricted receipt schema deterministically;
2. hash the canonical UTF-8 bytes with SHA-256;
3. publish the digest in both hex and `ni:///sha-256;...` form;
4. cite that locator in downstream notes unless the ceremony contract itself changed.

This is the right kind of archive growth.
It adds one tiny locator object, but it prevents repeated re-copying of the larger receipt body across many future handoff artifacts.

For this archive, the implementation can stay narrow and honest: the current receipt schema uses only objects, strings, and one integer schema version, so a restricted JCS-style canonicalization is enough to get a stable content address without pretending to be a universal JSON-signing framework.
