# Conflict resolution, precedence, and disagreement profiles are world contracts, not just quorum counts

Authorized speakers and explicit quorum rules are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what happened when overlapping authorities, valid-but-conflicting statements, or partially satisfied policies pointed in different directions**.

- `RS-GR-400` shows that the current TUF specification defines terminating delegations so clients stop considering later trust statements that match the delegated pattern, which means precedence is part of the security contract and not just metadata layout.
- `RS-GR-401` shows that current TUF supporting-class documentation makes delegated-role order define the order that target delegations are considered during search, so overlap resolution can depend on declared search order and not only on whether a role exists.
- `RS-GR-402` shows that CVE-2025-2886 arose because a TUF client failed to respect terminating delegations and delegation priority and therefore accepted information from a lower-priority delegation that should have been ignored, which makes precedence bugs visibly outcome-changing.
- `RS-GR-403` shows that current in-toto verification does not treat threshold as a pure count: threshold verification fails unless enough authorized functionaries both sign and **agree on the recorded materials and products**, so disagreement semantics belong in the verification contract itself.
- `RS-GR-404` shows that the current SCITT architecture allows multiple issuers to make different, even conflicting, statements about the same artifact and says relying parties may include or exclude statements from issuers to determine the accuracy of the collection, so conflict curation is a first-class relying-party responsibility.
- `RS-GR-405` shows that current Sigstore policy-controller API semantics treat multiple authorities within one policy as an `OR`, so one satisfied authority may be enough inside a given policy boundary.
- `RS-GR-406` shows that current Sigstore policy-controller admission semantics treat matched `ClusterImagePolicy` resources as `AND` while authorities within each policy remain `OR`, and also declare a configurable `no-match-policy`, so the same evidence set can pass, warn, or fail under different resolution profiles.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **precedence order, terminating / veto semantics, agreement requirements, AND-vs-OR composition, issuer-inclusion policy, or no-match fallback behavior** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “it had enough support” as the end of the story.

At minimum, it should distinguish between:

1. a world where any one valid signer, issuer, or policy match can admit a claim and conflicting evidence is effectively ignored;
2. a world with overlapping authorities, but where delegation order, first-match / last-match behavior, or termination semantics remain undocumented local lore;
3. a world where thresholds are published, but the archive does not preserve whether counted functionaries had to agree on the same materials, products, or predicate content;
4. a world where multiple issuers, statements, or policies can coexist, but the archive does not preserve whether they compose as `AND`, `OR`, `k-of-n`, veto, or configurable no-match fallback;
5. a world where future inheritors can replay the full disagreement profile — precedence order, termination or veto rules, agreement requirements, issuer-inclusion filter, and no-match / abstention handling — and see why one claim prevailed while another valid-looking claim was excluded.

These are different worlds.
They change whether future inheritors can merely see that support existed, reconstruct why one path had authority to terminate search, or detect that a later replay quietly flipped the outcome by changing conflict resolution rather than changing facts.

So conflict resolution, precedence, and disagreement profiles belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the precedence order for overlapping authorities, delegations, or policy matches, including whether any role or policy is terminating or veto-capable;
2. the exact composition rule across support sources: `AND`, `OR`, threshold, first-match, last-match, explicit veto, or configurable fallback when nothing matches;
3. whether concurrence requires agreement on the same subject, materials, products, or predicate content, or merely enough valid signatures;
4. how same-subject conflicting statements are grouped, filtered, superseded, or excluded by issuer, policy profile, or relying-party curation;
5. what happens under disagreement, abstention, missing receipts, or no matching policy: reject, warn, degrade, quarantine, escalate, or defer;
6. whether emergency or recovery modes alter precedence, bypass ordinary veto rules, or permit alternate conflict-resolution profiles.

Without that compact contract, future inheritors can mistake silent priority inversion, hidden fail-open composition, or disagreement suppression for Golden-Rule progress.
