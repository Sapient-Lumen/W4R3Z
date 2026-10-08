# Rev0992 audit

## Defect

A 4 MiB ranged walk retransmitted the complete 4,096-digest fixed-block target manifest on every response, while the receiver rebuilt and sorted the predecessor digest index at every block boundary. At the 4 TiB frontier, repeating only the eight-byte length and 64-byte digest entries after the first response admitted 309,237,350,400 bytes of avoidable framing, before optional-field and container overhead.

## Correction

Reconciliation protocol generation 5 binds the exact target manifest to a canonical digest. A cache-cold receiver gets the full bounded manifest; an exact same-process continuation may advertise that digest and receive a constant-size reference. The source re-proves its own manifest before honoring the reference, and the receiver requires its actual cache and validates every complete referenced block before durable staging. One cohesive predecessor cache retains the manifest and its digest-sorted index so later ranges do not allocate and sort 4,096 indices again.

## Adjacent audit/refactor

Target-manifest and predecessor-index caches now have explicit identities and bounded lifetimes. Restart cannot claim either cache and therefore bootstraps from a full manifest. A negative regression changes both referenced bytes and their transmitted chunk digest and proves rejection occurs before the durable staged prefix changes. The source audits and release verifier bind the complete protocol, service, TLS, CLI, metric, test, and documentation surface.

## Nonclaims

This remains fixed-block delta. Insertion-driven boundary shifts can collapse reuse. The revision does not claim content-defined chunking, cross-file discovery, a measured multi-terabyte peak-RSS result, Android, rename/move identity, or ENOSPC qualification.
