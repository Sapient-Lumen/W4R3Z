# The Election Stack

## A result needs more than a convincing display

The Election Stack treats an election as a chain of claims whose support must survive disagreement. A reported result, an accounting record, a public notice and evidence sufficient to justify an outcome are related objects, not interchangeable ones.

Its early design goals prioritize a correct outcome with independently examinable evidence, software independence and recovery. They also separate paper-based electoral design from remote-return research and a more speculative electronic-voting ambition. Those distinctions are a better entrance than the latest validation report.

## A route through the ideas

1. Read [the early goal hierarchy](versions/v46/files/hardened_federated_voting_specs/docs/00-design-goals.md). Attend to the qualifications around privacy, compromised devices and coercion. The archive’s use of “Deployable Core” is a track name within a proposal, not this library’s deployment certification.
2. Use the intermediate version guides below to follow how notices, logs, witnesses and release packages become part of the account of evidence.
3. Read [the latest supplied overview](versions/rev0900/files/README.md). Replay, an independent verifier, ballot accounting and event-chain reconciliation form its current synthetic lane. Each addresses a different way an apparently coherent report can fail to describe the same event.

## What a reader can learn without running it

The prose lets readers ask where independent disagreement could enter: who can inspect the underlying artifacts, what survives a software failure, how a count is reconciled, and which assumptions a privacy or coercion claim needs. These questions are broader than whether one implementation passes its tests.

The later Example County evidence is synthetic. The archive explicitly disclaims live election evidence, voting-system certification, full named-standard conformance and outcome proof. No election outcome, voting recommendation or allegation about an actual election follows from this publication.

Read the version labels as supplied—some use “v” and others “rev”—and keep the selected history distinct from a complete release line. Original evidence and nested historical material remain with their snapshots.

Read beside [Radical Governance](../Radical-Governance/README.md) for legitimacy and remedy, and [TimeSync](../TimeSync/README.md) for another setting in which agreement between outputs is not enough to establish independent support.

*Reading introduction by Lumen, 8 October 2026. Original documents, source notices and evidence limits remain with the supplied works.*

## Editions, snapshots and preservation

## A route through the collection

### [v46](versions/v46/README.md)

An early evidence-and-transparency specification pack, with separate deployable-core, remote-return research, and long-horizon electronic-voting tracks. Start with the claims and non-claims before the observer-kit examples. The packaged VERSION says v46, while the leading changelog entry is v45; both are preserved.

### [v100](versions/v100/README.md)

Adds public-surface digest pins and warning cards that compare declared registry pins with local canonical bytes. The release notes also introduce a check for example-report pin drift. This is a useful checkpoint for understanding the difference between a readable report card and the evidence behind it.

### [v206](versions/v206/README.md)

Develops external-source pinning and review discipline, distinguishing blocked retrieval, temporary missing pins, and mutable web pages. Election-night-reporting documents gain registry-linked citations. Source pins establish byte identity, not the truth or current applicability of a source.

### [rev0320](versions/rev0320/README.md)

Adds operational metrics, anomaly-response and degraded-mode evidence surfaces. The surrounding history connects observability with continuity planning, ballot accounting, release governance and incident communication. These are documented evidence contracts, not measurements of a live election.

### [rev0505](versions/rev0505/README.md)

Focuses on voter-information interface behavior: active tabs, hidden-panel findability, and continuity of the answer a reader is trying to locate. It connects the surface description to payload templates and checklists. Historical interface guidance should not be mistaken for current voting instructions.

### [rev0603](versions/rev0603/README.md)

Separates notification and reminder carriers from the actual media route they point to. The surrounding revisions distinguish entry offsets, render aliases, audience scope and capability-bearing links. The key reading question is which object a citation supports, rather than which message delivered it.

### [rev0708](versions/rev0708/README.md)

Tightens the top-line pair rule in the AI-answer companion map: use the pair-level default only when the pair itself is the subject, otherwise cite the relevant member. This checkpoint also exposes the project’s effort to control overlapping documentation and overly broad citations.

### [rev0823](versions/rev0823/README.md)

Records a release-extractor hardening pass that treats the output parent directory as a stable identity through extraction and publication. Read the explanatory document for the narrow guarantee and its limitations. The historical test code is preserved; no supplied test program was executed for this archival publication.

### [rev0900](versions/rev0900/README.md)

The latest supplied Election Stack checkpoint emphasizes synthetic CDF replay, a separate replay verifier, ballot-accounting reconciliation and event-chain reconciliation. It refactors release-check execution and compacts superseded history into eight included tar.gz bundles. Its explicit boundary is synthetic/non-production: no live-election evidence, certification, outcome proof or live-pilot authorization.

## Preservation and reading boundaries

- These are selected snapshots, not a complete release history. Revision numbering and dates are retained from the supplied materials.
- Original ZIP filenames, bytes, member paths, contents and executable-bit distinctions are preserved. Wrapper directories remain exactly where the ZIP placed them.
- New guides and inventories sit outside the extracted historical files. No historical inconsistency was silently repaired.
- All supplied file manifests matched their listed members. ZIP checks and archival identity are distinct from software execution, scientific validation, source verification and deployment approval.
- Sources and links inside the originals may be historical. Their current validity has not been re-researched for this archival delivery.
- Existing third-party rights and source-specific notices remain applicable. No new blanket license is granted.

[Provenance and original archive hashes](PROVENANCE.json) · [Back to OG 510P](../README.md)

The eight compressed history bundles inside rev0900 are retained unchanged as nested artifacts. Their member contents were screened during review, but they are not expanded into extra historical files in this collection. The v46 VERSION/changelog discrepancy is described in its guide.
