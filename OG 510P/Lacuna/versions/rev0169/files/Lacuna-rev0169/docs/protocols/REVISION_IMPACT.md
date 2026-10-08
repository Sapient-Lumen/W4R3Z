# Governed revision and impact review

## Why revision is a protocol

Replacing a latent-world fact can invalidate clues, motives, questions, disclosures, inherited worlds, and player-facing promises. Rev0149 removed silent exact-slot replacement. A truth-changing mutation requires a head-bound impact review and creates a new assignment record.

## Lifecycle

```text
1. request revision-impact for the active assignment
2. inspect blockers, burden, exposure, and explicit consequences
3. repair or retire blocking consequence custody, or fork the world
4. submit revise_world with the exact impact SHA-256
5. receive predecessor/successor lineage in the immutable ledger
6. inspect any surviving nonbinding consequence repair debt
```

## Review command

```bash
./lacuna revision-impact CUBE asn_secret > /tmp/impact.json
```

The report is `lacuna.revision-impact.v1` and contains:

- cube ID and review/base ledger head;
- target assignment and world status;
- explicit incoming and transitive outgoing consequences;
- a derived ambient footprint;
- deterministic traversal limits/completeness;
- blockers;
- a transparent burden breakdown;
- `impact_sha256` and the exact operation required.

## Digest binding

The digest covers the complete review core and the base head of the atomic change-set that will consume it. A separately committed intervening event makes it stale, even an apparently unrelated one. This avoids time-of-check/time-of-use drift and keeps the decision reproducible.

Operations earlier in the same atomic change-set are evaluated against current in-transaction projections while retaining that shared base-head value. This permits a source record and reviewed mutation to commit together, but any earlier operation that alters review-relevant state changes the recomputed digest and is refused.

A stale digest returns `stale-revision-impact`; no event is appended.

## Blockers

Current blockers are:

- inactive assignment;
- hard commitment;
- any active binding consequence incident to the assignment or reached through its outgoing assignment consequence graph;
- traversal truncation at deterministic graph limits.

A blocker is not automatically repaired. The host must choose whether to retire/relink custody, fork the world, or abandon the revision.

## Burden

The ordinal `lacuna.revision-burden.v1` policy scores named recorded components such as commitment level, selected-world status, assertion history, anchors, evidence, open questions, constraints, inherited descendants, cross-world consensus, and explicit consequences.

It is designed to answer “what recorded surface area should a reviewer inspect?” It does not answer “is this rewrite good?”

The output explicitly states that it is not:

- a probability;
- a utility value;
- a causal proof;
- a player-surprise estimate;
- a certificate of fairness.

## Ambient exposure versus explicit dependence

Ambient exposure is deliberately conservative. An assertion about the same claim may matter, but Lacuna does not pretend it was caused by the assignment.

Only a `consequence_link` asserts authored dependence. This distinction prevents the engine from turning every nearby detail into retroactive foreshadowing.

## Apply the revision

```bash
./lacuna world-revise CUBE asn_secret false \
  --assignment-id asn_secret_rev2 \
  --expected-impact-sha256 DIGEST_FROM_REVIEW \
  --reason "The surviving evidence favors the alternative explanation." \
  --commitment tentative \
  --commitment-basis planning
```

The successor must preserve the predecessor’s world, claim, timeline, and exact validity interval. Its truth must differ. It begins `tentative` or `soft`; a higher level must be reached through separate governed transitions.

The predecessor ends at the same sequence at which the successor is created. The successor stores:

- `revision_of_assignment_id`;
- `revision_reason`;
- `revision_impact_sha256`.

## Consequence disposition

Binding links must be repaired or retired before revision. A consequence replacement uses the separate digest-bound protocol in [`CONSEQUENCE_REPAIR.md`](CONSEQUENCE_REPAIR.md). Notice and material links do not vanish. After their premise ends they are reported as `orphaned-consequence` attention items and `repair_required=true` until deliberately retired or replaced.

The kernel does not guess whether an old promise should transfer to the successor. Automatic transfer would create a new causal claim without authorship.

## Atomicity and concurrency

Revision is submitted through the ordinary change-set path. The impact digest catches reviewed-state drift; the change-set expected head catches concurrent writes. Both use the same transaction base head. Any failure leaves both event ledger and projections unchanged.

## Nonclaims

- Revision lineage is not proof that the newer assignment is truer.
- A low burden does not imply artistic safety.
- A high burden does not forbid revision unless a blocker is present.
- The report does not inspect natural-language transcripts that the cube does not store.
