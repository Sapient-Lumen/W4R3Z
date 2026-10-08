# Successor-safe ceremony receipt package heads and redirects should collapse to compact catalogs

Once the archive has package heads for live package roots and redirect artifacts for superseded ones, there is still one cheap steward question left:

> What package families exist here, which head is live for each family, and which old package roots already redirect forward?

The individual head, lineage, status-card, and redirect objects already contain the raw answer, but they make a future steward browse several neighboring files just to discover the current package families in the archive.

A tiny **package catalog** should collapse that discovery into one machine-checkable object:

- one entry per retained successor-safe ceremony receipt family
- the live package head for that family
- the live package-status-card and authoritative package manifest
- the lineage record backing that head
- the active receipt-locator digest
- the count and index of superseded-package redirects already retained for that family

The catalog should use standard collection and typed-link semantics instead of archive-local labels:

- `item` for each current package-head entry exposed by the catalog
- `latest-version` for the current authoritative package manifest of a family
- `version-history` for the lineage record that explains the family history
- `status` for the live package-status-card resource

That keeps the archive small while giving a fresh inheritor one obvious archive entry point for successor-safe ceremony packages.
They do not need to guess whether there is one family or many, or browse multiple lineage files just to discover the live package roots currently worth opening.
