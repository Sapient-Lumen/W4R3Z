# EvidenceVault

## Making an acceptance judgement travel

EvidenceVault asks what another person needs to check a claim of acceptability without simply trusting whoever first announced it. A signed “pass” tells us who endorsed something. It does not, by itself, establish which artifact was checked, what passing meant, how many unsuccessful attempts preceded the result, or whether the authority and history supporting it are still applicable.

The project’s answer is to make the judgement travel with its replay boundary: the object, the rules, the relevant choices, and the evidence needed to reconstruct the decision. This is useful wherever evidence crosses an organizational or technical boundary: a proof leaves its prover, a software artifact reaches an admission service, or a reviewer inherits a decision made under an earlier policy. An acceptance verdict under a policy does not establish that the policy itself is morally justified. It is to make “acceptable under these rules, on this scope” mean the same thing to producer and downstream reader.

This entrance presents the rev0821 five-paper series and its retained research corpus. Begin with the [acceptability kernel](versions/rev0821/files/EvidenceVault-rev0821/papers/ev_acceptability_kernel.pdf), then the [interpretation bridge](versions/rev0821/files/EvidenceVault-rev0821/papers/ev_interpretation_profiles.pdf). The three shorter family notes show how that shared argument becomes concrete carriers rather than three unrelated notions of acceptance.

## What must accompany the result?

The kernel organizes the problem around four closure obligations. **Identity closure** binds the evidence to the exact object and decision scope, preventing a valid result for one release from being reused for a nearby release. **Semantic closure** fixes the policy, verifier meaning, schema, canonicalization, and composition rules. **Selection closure** exposes the choices that could have influenced the result. **Transparency closure** carries the required external consistency, publication, checkpoint, and freshness evidence.

These obligations work together. Imagine a producer offering an approval for a release. A correct signature on the wrong release does not help; neither does an authentic result interpreted under a more permissive policy. A favorable result found after undisclosed retries is different evidence from a result obtained under a fixed attempt budget. And receipts from incompatible log views cannot simply be assembled into one apparently coherent history.

The portable carrier therefore keeps judged scope, evaluator semantics, lineage or branch-invariance evidence, and history/validity conditions together with a replay slice. A claimed outcome is attached to that boundary, not substituted for it. Missing or unverifiable prerequisites remain non-authorizing. The kernel distinguishes ACCEPT, REJECT, and UNKNOWN; local diagnoses such as PENDING explain a blockage without becoming a softer route to acceptance.

## Search is part of the evidence

One of the series’ strongest ideas is that plurality can conceal two different problems: searching until something passes and counting correlated evidence as independent support.

A selection surface records the admissible menu, budget, stopping or escalation rule, randomness policy, and interpretation profile. Realized lineage explains which path actually ran. An attempt ledger records retries and outcomes; a search-budget certificate supplies either complete relevant accounting or a replayable upper bound on undisclosed admissible search. Alternatively, a branch-invariance certificate can establish that the hidden choice would not change the policy-relevant outcome.

Thus a producer cannot present the best of many attempts as though it were an unselected observation. Sequential evidence has the same issue: watching a stream until a favorable prefix appears is a choice of stopping point. If an anytime-valid statistic is the justification, the bundle must name its update and threshold rules and carry the corresponding stopping-safe witness, rather than merely use the vocabulary of sequential validity.

Nor do three differently named receipts necessarily provide three supports. Dependency profiles expose shared authority, interpretation, history, mechanism, and retry provenance. Threshold counting uses the largest accepting subset whose members satisfy the policy’s pairwise separation requirements, not the number of files. This does not magically establish independence; it makes the evidence for claimed separation an explicit replay obligation.

Support also has to survive **applicable counterevidence**. A revocation, rollback trigger, emergency rejection, or debt-limit blocker dominates until policy-valid discharge is carried. Its scope, authority, timing, and history must match the judgement being replayed. An old approval does not survive a later applicable supersession merely because it was once valid; hiding the blocker or making applicability uncheckable is not a repair.

## Meaning survives only when it is carried

The interpretation bridge explains why a digest identifies bytes but not their meaning. Its profile fixes the object language, canonicalization, semantic roles, operational conventions, and outcome algebra. Changing a schema, resolver, transcript ABI, or policy cannot silently preserve the old claim. Cross-profile reuse instead needs carried translation evidence: relevant equivalence, semantics-preserving re-encoding, or authorized revalidation.

Governed replay adds a coherent history view, live scoped authority, satisfied temporal conditions, and declared transparency obligations. A policy-relative verdict must bind both object and policy digests and carry a witness for that target. A conservative policy ratchet has a precise direction: where predecessor checks remain or become stronger and new clauses add obligations on the same scope, successor acceptance implies predecessor acceptance, not the reverse.

The bridge also addresses a practical tension: readers need compact views, while replay needs context. Its replay slice combines visible evidence, commitments to omitted load-bearing objects, a digest-and-role manifest, the interpretation profile, and residual obligations. A shorter view may omit material justified as irrelevant to its scope, but it may not erase unresolved prerequisites.

The conservative projection claim is conditional on fail-closed, information-monotone replay: replacing necessary information with unknowns or commitments must not manufacture authorization. Acceptance of the shorter view then implies acceptance of the fuller state. A fast front claiming the authority of a fuller audit additionally needs same-scope conservative-comparison evidence, including relevant branch choices, unless policy establishes that the fuller role is unnecessary. A convenient URL or signed summary alone supplies neither condition.

## Three families, one replay discipline

[StreamFold / dOCF](versions/rev0821/files/EvidenceVault-rev0821/papers/ev_streamfold.pdf) specializes this model for recursive runs. Its signed manifest binds statements, public inputs, replay blobs, soundness parameters, retry history, and orchestration. Authenticated run views provide front or full roles on that same manifested run. Exact field, aggregation, and repetition choices matter; they are not interchangeable implementation details.

[zk-RTP](versions/rev0821/files/EvidenceVault-rev0821/papers/ev_zkrtp.pdf) uses evidence packages bound to a bundle, verifier, policy, resolver/profile, and checkpoint context. Support manifests distinguish portfolios, whose contributions need dependency-aware counting, from core/boundary pairs that are jointly required complementary obligations. Expanding those members returns to the kernel’s algebra rather than creating a second acceptance rule.

[PACT / OCF](versions/rev0821/files/EvidenceVault-rev0821/papers/ev_pact_ocf.pdf) carries transition, operational, or admission decisions in a scoped package. Admission adds an artifact/obligation manifest and residual deployment conditions, including compensating controls, debt blockers, or repair/discharge material. A change of presentation cannot remove those conditions while preserving the same claim.

## Read an actual prototype

The [PACT replay-pack verifier](versions/rev0821/files/EvidenceVault-rev0821/sources/pact/PACT_workdir/demos/verify_replay_pack.py) makes the binding story inspectable. It recomputes a manifest-derived run root, verifies signed run and policy-decision statements against that root, and checks Merkle memberships for a selectively disclosed store object and a committed view. The [demo pack](versions/rev0821/files/EvidenceVault-rev0821/sources/pact/PACT_workdir/replay_pack/README.md) supplies the corresponding materials.

That is a concrete illustration, not a full PACT implementation: the source explicitly says so, uses assertions for several checks, and signs payload-type plus a NUL plus payload rather than production DSSE PAE. Those prototype choices should not be confused with production DSSE interoperability.

The [complete original ZIP](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/evidencevault-rev0821) preserves the supplied curated corpus, including material beyond the browsable selections. “Complete” refers to that supplied archive, not every upstream project: the [source index](versions/rev0821/files/EvidenceVault-rev0821/SOURCE_INDEX.md) distinguishes retained roots from curated artifacts and references. Original component rights and notices remain applicable and are retained.

[Edition contents and download](versions/rev0821/README.md) · [Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
