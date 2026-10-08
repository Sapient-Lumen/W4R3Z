# Pruning policy

The working cube is not the preservation archive. Prior revisions, bulky seed copies, and specimen poem texts stay outside the release unless the human explicitly asks for a preservation bundle.

Keep receipts, hashes, digests, and registries. Prune duplicate archives and transient build outputs.

## Turn-local revision constructors

Root-level `do_rev####*.py` migration scripts depend on a particular parent tree and are not standalone source for the current cube. They are transient scaffolds: prior release archives preserve them historically, while current manifests and packages exclude them. The shared `tools/release_tree.py` policy is authoritative for that exclusion and rejects any such constructor found inside a release zip.
