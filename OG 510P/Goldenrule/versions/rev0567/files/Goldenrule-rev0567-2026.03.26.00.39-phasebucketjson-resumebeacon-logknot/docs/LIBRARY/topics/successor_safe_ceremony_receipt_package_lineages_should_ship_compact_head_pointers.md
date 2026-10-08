# Successor-safe ceremony receipt package lineages should ship compact head pointers

Once a successor-safe ceremony receipt archive already has package manifests, supersession records, and a lineage object, the next stewarding failure mode is no longer missing history; it is slow discovery. A future inheritor often wants the cheapest possible answer to one question: which package root is authoritative right now?

A lineage record is the right audit object, but it is not the cheapest discovery object. RFC 5829 defines standard link-relation names such as `latest-version`, `version-history`, and `predecessor-version` for navigating versioned resources, and RFC 9264 shows that sets of related links can live in a compact standalone document rather than being embedded in a larger representation. `RS-GR-537`, `RS-GR-538`, and `RS-GR-539` therefore support one small archive-local package-head pointer that names:

- the current authoritative package manifest
- the lineage object that justifies that head
- the live review-verdict artifact that says whether citation continues
- the live citation-advisory artifact that says what downstream stewards should do
- the immediate predecessor manifest when a prior head exists

That head pointer is not a replacement for lineage. It is a discovery surface over lineage. The archive should therefore preserve both: a lineage object for ordered authority history, and a compact package-head pointer for immediate current-state discovery.
