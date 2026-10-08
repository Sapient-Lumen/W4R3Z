# License decision blocker

No open-source, open-data, redistribution, or reuse license is granted by this file or by the current archive metadata.

The current archive is mechanically verifiable, but it lacks an explicit root `LICENSE`, `COPYING`, or `NOTICE` file. The RO-Crate root license value has been changed from the vague `See README.md` pointer to `NOASSERTION` so downstream readers do not mistake an unresolved pointer for a grant.

Before public publication or redistribution, the archive owner should choose and encode one of these positions:

1. A permissive archive-level license for project-authored material, with separate upstream component notices.
2. A restricted/internal-evaluation license if redistribution is not intended.
3. A mixed-license package layout where each retained upstream family has an explicit declared license, exception, or removal decision.

Minimum canonical repair: add root `LICENSE`, add root `NOTICE`, update RO-Crate license metadata to a concrete license entity or URL, and replace component `NOASSERTION` entries in `RIGHTS/component_license_ledger.json` and `SBOM/EvidenceVault-file-inventory.spdx.json`.

This is not legal advice.
