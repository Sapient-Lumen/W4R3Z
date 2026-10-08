## rev0499 operating addendum — handoff graph revisions
Use a **handoff graph** revision when the missing work is not a new seam, packet, wedge, journey, or shipset, but an explicit answer to:
- what artifact should move from one strong seam into another;
- what transformation is allowed in the middle;
- what receipt should emerge at the end; and
- what stable versus unstable/service posture the edge depends on.

Minimum same-revision updates:
- `design/epic-contribution-handoff-graph-2026Q1.md`
- `meta/HANDOFF_GRAPH_PROTOCOL.md`
- `ledgers/top-band-handoff-graph-v0/README.md`
- `ledgers/top-band-handoff-graph-v0/handoffs.json`
- `tools/check_handoff_graph.py`
- front-door continuity rails if the default answer changed
- mirror updates, manifest regeneration, and archive-doctor refresh

## rev0498 — operating rail for kernel-shipset / first-repo-shape canon
When a revision touches the archive's strongest worthy contributions and is mainly about **what exact first repo shape a small team should build**, it must now keep **kernel shipset / first-repo-shape canon** separate from rank, wedge, journey, watchcard, and charter work.

Minimum same-revision steps:
1. state explicitly that the change is about first shipset canon rather than a broad rerank;
2. add or refresh `design/epic-contribution-kernel-shipset-ledger-2026Q1.md` and `meta/KERNEL_SHIPSET_LEDGER_PROTOCOL.md` when the shared rules changed;
3. add or refresh `ledgers/top-band-kernel-shipsets-v0/shipsets.json` and its README;
4. refresh the nearest affected prose kernel brief in `kernels/top-band-v0/` if the first-build answer changed materially;
5. add or refresh `tools/check_kernel_shipsets.py` and wire it into hygiene and archive-doctor;
6. refresh the front-door and continuity rails if the default answer changed; and
7. mirror refreshed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, and rerun the archive doctor.

Refusal rule:
- do not let a revision answer “what should we build first?” with only prose when the actual first shipset canon changed.

## rev0497 operating addendum — prefer journey-layer edits when the missing thing is cross-seam workflow composition
If a new continue-research pass mainly discovers that the repo still cannot say **which repeated operator moment a set of strong seams should change together**, prefer a decision-journey revision over any of the following:
- inventing a fresh seam;
- rewriting the broad ladder;
- widening one seam into a platform story; or
- duplicating wedge or packet prose.

A good decision-journey revision normally leaves behind:
- one broad design note,
- one machine-readable journey ledger,
- one structural checker,
- refreshed routing/continuity rails,
- and updated archive-doctor coverage.


# Revision operating protocol addendum (rev0496)

When a revision touches the archive's strongest worthy contributions and is mainly about **how they first become real for users**, it must now keep **launch-wedge / first-proof-path discipline** separate from rank, watchcard posture, packet posture, stewardship, and canon.

Minimum discipline:
1. state which seams the revision assigned or changed wedges for;
2. say who the first real user is and what decision window makes the wedge credible;
3. name the initial artifact or surface that enters that moment;
4. name the proving ground and success signal that would count as honest first proof;
5. say explicitly what broader product temptation is still refused even if the wedge works; and
6. do not let “this could become big” impersonate “this has a believable entry point.”

# Revision operating protocol addendum (rev0495)

When a revision touches the archive's strongest repeated claims and is mainly about **whether those claims still hold**, it must now keep **hypothesis-ledger / falsifier-gate discipline** separate from rank, watchcard posture, packet posture, stewardship, and canon.

Minimum discipline:
1. state which hypothesis cards the revision touched;
2. say whether each affected claim was **confirmed**, **narrowed**, **degraded**, **superseded**, or **retired**;
3. distinguish source refresh from claim-state change;
4. refresh the nearest watchcard, packet, stewardship, canon, or hygiene assets named by the affected cards;
5. say explicitly what did **not** change; and
6. do not let a fresh source change impersonate a claim downgrade until the card's own triggers are actually met.

# Revision operating protocol addendum (rev0494)

When a revision touches the archive's top worthy contributions and is mainly about **fast-moving imported truth**, it must now keep **hot-substrate watchcard discipline** separate from rank, packet posture, stewardship, and canon.

Minimum discipline:
1. state whether the change is primarily a watchcard, packet, charter, canon, or hygiene move;
2. emit or refresh at least one watchcard when the dominant change is fast substrate drift;
3. say what truths are imported, what the source still does **not** prove, and what downstream assets should care;
4. say explicitly what did **not** change;
5. do not let a fast source change impersonate a packet or canon rewrite automatically.

# Revision operating protocol addendum (rev0493)

When a revision touches the archive's top worthy contributions and is mainly about **how the repo should keep them current**, it must now keep **control-loop / cadence discipline** separate from rank, packet posture, stewardship, and canon.

Minimum discipline:
1. State whether the change is primarily a **hot substrate watch**, **decision-packet**, **charter/stewardship**, **canon**, or **archive hygiene** move.
2. Say explicitly what did **not** change.
3. Emit the artifact family that belongs to the dominant loop.
4. Do not let a hot source change impersonate a canon rewrite.
5. Do not let hygiene-only work impersonate a packet or charter change.
6. The broad ladder is unchanged: future “what loop should this change trigger?” answers should route through `design/epic-contribution-portfolio-control-loop-2026Q1.md` before rewriting canon.


## rev0492 revision addendum
When a revision materially changes the repo's answer to **where a worthy contribution should live or how it should mature**, update the stewardship/graduation canon in the same revision:
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `meta/STEWARDSHIP_AND_GRADUATION_PROTOCOL.md`
- `RESEARCH_LOG.md`
- `meta/LATEST_REVISION_FILESET.md`
- `atlases/portfolio-source-atlas-v0/sources.json`

Do not let “should move upstream”, “should stay external”, “should become official”, or “should be service-side” appear in canon prose without an explicit split-home and authority explanation.

## rev0491 — operating-surface revision addendum
If a revision is mainly about **how the strongest seams should compose as one family in theory and practice**, it should now say explicitly:
1. what shared verbs became clearer;
2. what receipt or artifact roles should repeat;
3. what negative-state posture is required across seams;
4. what residency shapes remain credible;
5. what existing seams gain the most from the shared grammar; and
6. what tempting control-plane or framework shape should be refused.

Default rule:
- do not treat a new shared grammar as a new top-band seam by default;
- do not let one current upstream command or API define the whole archive’s family language;
- and prefer companion-first evidence/review/replay/renew families before hosted-platform extrapolation.

## rev0490 — worthy-repo-buildout operating addendum
When a revision is explicitly about **continuing research and constructing the archive further**, the minimum operating sequence is now:
1. re-open the current routing/front-door files and the latest live-refresh note;
2. gather fresh primary sources that change practical shape rather than merely restating pain;
3. decide whether each fresh signal belongs in **broad ranking**, **current packet posture**, **repo buildout order**, or **fold-under-parent mapping**;
4. add or refresh the design/meta notes that preserve those distinctions;
5. update the front-door ranking notes and continuity rails in the same revision;
6. refresh the source atlas when a source becomes a repeated practical anchor;
7. mirror refreshed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, and rerun the archive doctor.

Refusal rule:
- do not accept a “continue the repo” revision that mostly adds new seam names, slogans, or atmosphere while leaving theory/practice shape and continuity rails untouched.

## rev0489 operating addendum — live ecosystem refreshes must separate strategy, current posture, and source-candor
When a revision is mainly about **what the latest archive plus latest official Rust signals imply right now**, do all of the following in the same revision:
1. state whether the change is about **broad strategic importance**, **current delivery posture**, **meta-hygiene**, or some mix of the three;
2. add or refresh the nearest live-refresh synthesis note;
3. add or refresh the nearest live-refresh protocol note if the revision changes archive-operating behavior;
4. record the fresh sources and exact source dates in `RESEARCH_LOG.md` and/or `atlases/portfolio-source-atlas-v0/sources.json`;
5. say explicitly what did **not** change in the broad ladder and current packets;
6. refresh `meta/LATEST_REVISION_FILESET.md` and `meta/ARCHIVE_MANIFEST.md`; and
7. mirror changed files under `archive/`.

Do not let one latest-signals refresh masquerade as a new broad ladder or a silent packet rewrite.

## rev0488 operating addendum — schema-governed revisions
When a revision adds or materially changes machine-readable artifact families for already-earned kernels, do all of the following in the same revision:
1. update the nearest design note and protocol note;
2. add or refresh schema files plus a schema-hygiene/index file;
3. add or refresh bound specimen payloads;
4. add or refresh the schema validator tool;
5. wire the validator into `tools/hygiene.py` and `tools/archive_doctor.py`;
6. update `specimens/README.md`, `meta/LATEST_REVISION_FILESET.md`, and `meta/ARCHIVE_MANIFEST.md`; and
7. mirror changed schema/specimen/protocol files under `archive/`.

Do not treat a new example JSON file as complete until the validator passes against a schema family.

## rev0487 — operating rail for kernel fixture packs
If a revision is mainly about **what replayable scenario should drive a top-band kernel's witness output**, it should distinguish:
- **contract refresh** — the surface changed;
- **witness refresh** — the example output changed;
- **fixture refresh** — the replayable input scenario or expected checks changed;
- **broad note refresh** — ranking, grouping, or design theory changed.

Default rule:
- do not let a new replay assumption hide inside witness prose or contract cleanup.
- if the revision wants to say what scenario and checks should generate the archive's endorsed outputs, leave behind a fixture card.


# Revision operating protocol addendum (rev0486)

When a revision touches the archive's **top-band practical build agenda** and is mainly about **what a contract-governed kernel should look like when exercised**, it must now keep **example artifact witness posture** separate from rank, verdict, repo shape, slice scope, and contract surface.

Minimum discipline:
1. State whether the change is about **importance**, **verdict posture**, **repo shape**, **slice scope**, **contract surface**, or **contract witness / example artifact posture**.
2. Name the governing live packet, kernel brief, slice note, and contract note for every witness bundle.
3. Say explicitly what the witness example is allowed to prove and what it is not allowed to prove.
4. Keep at least one negative or partial-state example visible in every witness family.
5. Keep stable-only versus unstable-enhanced example posture visibly separate where relevant.
6. Refuse witness creation for `hold` candidates unless the blocker changed materially.
7. Refresh `specimens/README.md`, `meta/SPECIMEN_CORPUS_PROTOCOL.md`, and `meta/LATEST_REVISION_FILESET.md` in the same revision.

Failure mode to refuse:
- a new example corpus that looks concrete but silently erases negative states, unstable-import caveats, or route-specific uncertainty.

# Revision operating protocol addendum (rev0485)

When a revision touches the archive's **top worthy contributions** and is mainly about **what exact command/file/schema surface a bounded kernel should expose**, it must now keep **kernel interface contract discipline** separate from rank, verdict posture, repo shape, slice scope, charter shape, and stage-gate posture.

Minimum discipline:
1. State whether the change is about **importance**, **current verdict**, **repo shape**, **owner shape**, **stage gate**, **kernel slice**, or **kernel interface contract**.
2. Say explicitly which live packet, kernel brief, and slice note govern the new contract.
3. Say explicitly what commands/files/cards/receipts are public in `contract0`.
4. Say explicitly what stable imports exist and what experimental imports remain caveated.
5. Say explicitly what negative or unsupported states must survive as first-class receipts.
6. Say explicitly what wider protocol, hosted API, or upstream claim is still refused.
7. The broad ladder is unchanged: future “what exact surface should this kernel expose?” answers should route through `design/epic-contribution-kernel-interface-contracts-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0484)

When a revision touches the archive's **top worthy contributions** and is mainly about **what lands first inside a bounded kernel**, it must now keep **kernel slice / thin-milestone discipline** separate from rank, verdict posture, repo shape, charter, and stage-gate posture.

Minimum discipline:
1. State whether the change is about **importance**, **current verdict**, **repo shape**, **owner shape**, **stage gate**, or **kernel slice / first milestone**.
2. Say explicitly which kernel is governing the slice.
3. Say explicitly what belongs in slice 0 and what is postponed.
4. Say explicitly what proving grounds and failure receipts must ship with slice 0.
5. Say explicitly what next-slice trigger earns wider scope.
6. Do not let “this is in the v0 brief” impersonate “this should land first”.
7. The broad ladder is unchanged: future “what lands first?” answers should route through `design/epic-contribution-kernel-slices-2026Q1.md` before rewriting canon.

## rev0483 — operating rail for first-build kernel briefs
If a revision is doing top-band practical-build work, it should distinguish:
- **packet refresh** — verdict posture changed or was reissued;
- **dossier refresh** — current working posture changed or was restated;
- **kernel refresh** — the first honest repo shape changed;
- **broad note refresh** — ranking, grouping, or design theory changed.

Default rule:
- do not let a new first-build shape hide inside packet prose or broad synthesis.
- if the revision wants to say what a top-band candidate should actually ship first, leave behind a kernel brief.

## rev0482 — operating rail for live current-verdict packets
If a revision is doing present-tense top-band judgment, it should distinguish:
- **dossier refresh** — current working posture changed or was restated;
- **live packet refresh** — the actual current verdict artifact changed or was reissued;
- **specimen refresh** — packet grammar changed;
- **broad note refresh** — ranking, grouping, or design theory changed.

Default rule:
- do not let a new live verdict hide inside a dossier refresh or prose cleanup.
- if the revision wants to say what the repo would actually decide now, leave behind a packet.

## rev0481 — dossier continuity rail
The archive now has enough ranking, packet, and specimen canon that the next continuity failure mode is easy to name:
future revisions can still sound grounded while reconstructing the leaders' **current posture** from scattered notes, producing subtle drift in verdict, next move, or refusal shape.

Default rule:
- if a revision materially updates a top-band candidate's current posture but leaves no refreshed **dossier** or does not say which dossier it used as its starting point, treat the revision as continuity-lossy even if the prose is strong.


## rev0480 — operating rule for packet-specimen revisions
When a revision is mainly about **showing what a real packet looks like**, it must:
1. name the specimen(s) being added or refreshed;
2. say what verdict posture each specimen is teaching;
3. separate imported evidence from archive inference;
4. carry source-candor notes for synthesis, roadmap/prototype, operational, and governance/support sources as needed;
5. keep missing proof and refused larger forms visible;
6. update `specimens/README.md`, `meta/LATEST_REVISION_FILESET.md`, and `meta/ARCHIVE_MANIFEST.md` in the same revision; and
7. mirror new specimen files under `archive/`.

Do not let a packet-specimen revision become another broad ranking memo.


# Revision operating protocol addendum (rev0479)

When a revision touches the archive's **top worthy contributions** and is mainly about **what to do with them now**, it must now keep **review packet / requested verdict discipline** separate from rank, proof burden, charter shape, and stage-gate posture.

Minimum discipline:
1. State whether the change is about **importance**, **delivery shape**, **program-spec**, **charter**, **stage gate**, or **review packet / verdict discipline**.
2. Say explicitly what packet is being reviewed: identity, why-now signals, kernel/artifact family, stage/proof status, decision improved, proving grounds/negative states, owner shape, adjacency, bounded v0, and requested verdict.
3. Use one explicit verdict for each reviewed candidate: **advance**, **deepen**, **merge**, **hold**, **fold**, or **kill**.
4. Say explicitly what tempting larger build is still refused.
5. Say explicitly what evidence expires and what trigger requires packet reissue.
6. The broad ladder is unchanged: future “what should we do with this candidate now?” answers should route through `design/epic-contribution-review-packets-2026Q1.md` before rewriting canon.


# Revision operating addendum (rev0478)

When a revision claims to make a top worthy program **more practical**, **closer to launch**, or **ready to widen**, require four explicit answers:
1. what stage the program is currently in;
2. what next gate would honestly earn promotion;
3. what proof budget has actually been earned so far; and
4. what tempting broader promise is still premature and should be refused.

Default rule:
- if a revision sounds like “this should now become bigger” but does not state stage, gate, budget, and refused premature promise, treat the revision as operating-lossy even if its prose is strong.

# Revision operating protocol addendum (rev0477)

When a revision touches the archive’s **“how does this worthy program become real?” answer**, it must now keep **program charter deepening** separate from broad rank, practical build shape, macro-program grouping, program-spec deepening, and frontier posture.

Minimum discipline:
1. State whether the change is about **broad rank**, **practical build shape**, **macro-program grouping**, **program-spec deepening**, **program-charter deepening**, **frontier posture**, or **meta-hygiene**.
2. Say explicitly where the first honest implementation **lives**.
3. Say explicitly what the **owner shape** is.
4. Say explicitly which **pilot partners** make the first results believable.
5. Say explicitly what the **first shipset** is and what recurring **maintenance envelope** it assumes.
6. Say explicitly what the **narrow upstream asks** are and what is **not** being asked for yet.
7. Say explicitly what the **graduation / fold / kill rules** are.
8. Say explicitly what **wrong launch pattern** is being refused.
9. Refresh `meta/LATEST_REVISION_FILESET.md` and the routing layer in the same revision.

Failure mode to refuse:
- a new “practical” program note that still leaves the owners, pilot partners, and maintenance burden to the reader’s imagination.

# Revision operating protocol addendum (rev0476)

When a revision touches the archive’s **“what must each top macro-program actually contain?” answer**, it must now keep **program-spec deepening** separate from broad rank, practical build shape, macro-program grouping, and frontier posture.

Minimum discipline:
1. State whether the change is about **broad rank**, **practical build shape**, **macro-program grouping**, **program-spec deepening**, **frontier posture**, or **meta-hygiene**.
2. Say explicitly what the **kernel artifact family** is.
3. Say explicitly which **import surfaces** are in bounds and what caveats travel with them.
4. Say explicitly which **proof assets** and **proving grounds** make the note reviewable.
5. Say explicitly what the **bounded v0** is and what it deliberately does not do.
6. Say explicitly what **exit criteria** must be met before widening.
7. Say explicitly what **wrong shape** is being refused.
8. Refresh `meta/LATEST_REVISION_FILESET.md` and the routing layer in the same revision.

Failure mode to refuse:
- a new “reference architecture” note that is still just a renamed wish list with no kernel, no proof assets, and no refusal clause.

# Revision operating protocol addendum (rev0475)

When a revision touches the archive’s **broad “what should this repo actually organize itself around?” answer**, it must now keep **macro-program grouping** separate from broad rank, practical build shape, frontier posture, and seam-local blueprint deepening.

Minimum discipline:
1. State whether the change is about **broad rank**, **comparative axis**, **practical build shape**, **macro-program grouping / fold**, **frontier posture**, or **meta-hygiene**.
2. Say explicitly which strong seams are being **folded under stronger parents** and which remain separate.
3. Say explicitly what is being **refused as a top-band answer** rather than merely ignored.
4. If a new broad note is being added, say why an existing broad note or seam-local blueprint could not carry the change.
5. Refresh `meta/LATEST_REVISION_FILESET.md` and the routing layer in the same revision.

Failure mode to refuse:
- a new “top missing things in Rust” note that only rephrases existing canon while adding one more front-door reading path.

# Revision operating protocol addendum (rev0474)

When a revision touches the archive's **broad “what should we actually build?” answer**, it must now keep **practical build shape** separate from rank, frontier posture, and abstract desirability.

Minimum discipline:
1. State whether the change is about **broad rank**, **practical build shape**, **hidden multiplier shape**, **urgent bridge shape**, **program/consortium shape**, or **continuity/meta-hygiene**.
2. Say explicitly whether each major candidate is being treated as a **report/pack family**, **acceptance commons**, **reviewable recommendation layer**, **reference/substrate multiplier**, **local-first boundary bridge**, or **stewarded program**.
3. Say explicitly what wrong shape is being refused: framework empire, dashboard theater, daemon/control-plane fantasy, badge farm, or assistant-memory canon.
4. Leave behind a fast continuity ledger in `meta/LATEST_REVISION_FILESET.md` when broad synthesis or routing changes.
5. Do not let one neat product surface silently erase the steward, proving-ground, or artifact-family story.
6. The broad ladder is unchanged: **Build-State Evidence** still wins overall; future practical-build answers should route through `design/practical-epic-contribution-briefs-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0473)

When a revision touches the archive's **top worthy contributions** and is mainly about **how quickly they can learn something truthful after a change**, it must now keep **learning clock / time-to-truth discipline** separate from rank, proof burden, renewal burden, reversibility, and decision rights.

Minimum discipline:
1. State whether the change is about **importance**, **proof burden**, **renewal burden**, **reversibility**, **decision rights**, or **learning clock / feedback tempo**.
2. Say explicitly which learning-clock family is in scope: **same-day local truth**, **cross-invocation / per-commit truth**, **release-train truth**, **tuple-matrix acceptance truth**, **incident / route-owner truth**, or **institutional / program truth**.
3. Say explicitly what the **fastest truthful loop** is.
4. Say explicitly what the **slower graduation loop** is before stronger defaults, canon claims, or wider support claims are justified.
5. Say explicitly what **synthetic proving ground** avoids waiting for live fallout, rare incidents, or broad ecosystem regressions.
6. Do not let one prototype, one benchmark screenshot, one nightly success, one operator anecdote, or one institutional sponsor silently decide the learning clock for a seam.
7. The broad ladder is unchanged: future time-to-truth answers should route through `design/epic-contribution-learning-clock-map-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0472)

When a revision touches the archive's **top worthy contributions** and is mainly about **how safely they should begin, how hard they are to undo, or what kind of ratchet they represent**, it must now keep **reversibility / blast radius** separate from rank, boundary fit, decision rights, proof burden, and support bundle.

Minimum discipline:
1. State whether the change is about **importance**, **boundary fit**, **decision rights**, **proof burden**, **support bundle**, or **reversibility / blast-radius discipline**.
2. Say explicitly which reversibility family is in scope: **advisory replayable probe**, **opt-in gate**, **default with escape hatch**, **operator-enforced boundary**, or **governance / standards ratchet**.
3. Say explicitly what the first rollback, bypass, or exception path is.
4. Say explicitly what artifact still survives after rollback: receipt, diff, witness result, exemption record, or staged rollout log.
5. Do not let one useful prototype silently become a hard default or social policy without naming the ratchet.
6. The broad ladder is unchanged: future rollout-shape answers should route through `design/epic-contribution-reversibility-map-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0471)

When extending the archive around **top worthy Rust contributions under who-must-agree, consensus-drag, local-first-versus-coalition, or operator-versus-upstream execution questions**, remember:

1. The missing comparative layer is not another rank rewrite and not another support-bundle rewrite.
2. The missing comparative layer is the **decision-rights map** that keeps importance, support bundle, boundary fit, proof burden, renewal burden, and consensus drag separate while making them reviewable together.
3. Always keep these truths separate:
   - unilateral / single-team value truth
   - local-first value with narrow upstream asks truth
   - operator / service-owner opt-in truth
   - cross-tool / tuple-consensus truth
   - consortium / standards / governance truth
4. Do not let one champion, one sponsor, one polished prototype, one toolchain component, or one working-group mention silently decide how many parties must agree before a seam becomes real.
5. Do not let “important” impersonate “fast to move”, do not let “upstream champion exists” impersonate “ecosystem consensus exists”, and do not let one local pilot impersonate cross-tool agreement.
6. The broad ladder is unchanged: **Build-State Evidence** still wins overall and now also as the clearest low-consensus local-first build; **Semantic Context / Tooling Contract / Shared Spine** remain the clearest low-consensus hidden multipliers; **Package Intake Gateway** remains the clearest operator bridge; **Feedback Loop / Debuggability Acceptance** remains the clearest cross-tool consensus seam; and **Safety-Critical Readiness Commons** remains the clearest consortium-grade seam.

# Revision operating protocol addendum (rev0470)

When a revision touches the archive's **top worthy contributions** and is mainly about **where a contribution should live**, it must now keep **residency / boundary fit** separate from rank, proof burden, support bundle, and incubation vehicle.

Minimum discipline:
1. State whether the change is about **importance**, **delivery shape**, **incubation vehicle**, **proof burden**, **support bundle**, **renewal burden**, **distortion risk**, or **boundary fit / residency**.
2. For every serious candidate, say explicitly which of these it is first: **companion-first layer**, **companion with narrow upstream asks**, **consortium/editorial commons**, **operator bridge**, or **upstream substrate/stabilization program**.
3. Do not let “important” silently become “merge it into Cargo/rustc/docs.rs”.
4. Do not let upstream aura silently substitute for proof, maintenance, or local-fit realism.
5. For every new comparative recommendation, prefer saying the **narrowest upstream primitive** the companion layer needs rather than asking upstream to absorb the whole product.
6. The broad ladder is unchanged: **Build-State Evidence** remains the strongest broad first build; future companion-vs-upstream answers should route through `design/epic-contribution-boundary-map-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0469)

When a revision touches the archive's **top worthy contributions** and is mainly about **how they can become dishonest while still looking successful**, it must now keep **distortion risk** separate from rank, proof burden, renewal burden, and support bundle.

Minimum discipline:
1. State whether the change is about **importance**, **proof burden**, **renewal burden**, **support bundle**, or **distortion risk / false-success discipline**.
2. Say explicitly which distortion family is in scope: **surface overread**, **tuple extrapolation**, **projection becomes canon**, **boundary collapse**, **Goodhart / scorecard corruption**, or **stewardship theater**.
3. Say explicitly what weak surface is being imported: stable/versioned contract, unstable prototype, best-effort hint, human-readable output, or editorial summary.
4. Say explicitly what false-success launch pattern is being refused.
5. Do not let one pretty UI, one benchmark hero number, one green badge, one supported tuple, or one institutional sponsor silently count as a solved ecosystem seam.
6. The broad ladder is unchanged: future false-success and anti-overclaim answers should route through `design/epic-contribution-distortion-risk-map-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0468)

When a revision touches the archive's **top worthy contributions** and is mainly about **what it takes to keep them honest after launch**, it must now keep **renewal burden** separate from rank, proof burden, bet size, and support bundle.

Minimum discipline:
1. State whether the change is about **importance**, **delivery shape**, **incubation vehicle**, **proof burden**, **bet size**, **support bundle**, or **renewal burden / upkeep cadence**.
2. Say explicitly which renewal family is in scope: **release-cadence evidence**, **tuple-matrix acceptance**, **editorial/default freshness**, **operational / incident**, **consortium / stewardship**, or **substrate watch**.
3. Say explicitly what part of the upkeep can be automated and what part still requires named human review or operations.
4. Say explicitly what expires, must be rerun, or needs scheduled review.
5. Do not let one successful v0 silently count as a sustainable maintenance plan.
6. The broad ladder is unchanged: future upkeep-shape answers should route through `design/epic-contribution-renewal-burden-map-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0467)

When a revision touches the archive's **top worthy contributions** and is mainly about **what support each one should concretely ask for**, it must now keep **support bundle** separate from rank, vehicle, proof burden, and bet size.

Minimum discipline:
1. State whether the change is about **importance**, **delivery shape**, **incubation vehicle**, **proof burden**, **bet size**, **compounding**, or **support bundle / ask discipline**.
2. Say explicitly who is being asked first: **upstream teams**, **maintainers**, **companion team**, **operators/vendors**, **consortium/interoperability group**, or **Foundation/institutional support**.
3. Say explicitly what the ask contains: review windows, maintainer time, exemplar access, tuple coverage, neutral convening, fiscal sponsorship, or something else concrete.
4. Say explicitly what is **not** being asked for yet.
5. Do not let a budget line silently substitute for upstream review, exemplar access, or coalition commitments.
6. The broad ladder is unchanged: future ask-shape answers should route through `design/epic-contribution-support-bundle-map-2026Q1.md` before rewriting canon.


# Revision operating protocol addendum (rev0465)

When a revision touches the archive's **shared spine / stage-0 portfolio glue**, it must now keep **shared outer contract** separate from **seam-specific payload** and from **later evidence products**.

Minimum discipline:
1. State whether the change is about **stage-0 shared-spine execution**, **later evidence**, **boundary bridge**, or **consumer/frontier widening**.
2. Say explicitly which artifact roles changed: **canonical pack**, **brief/handoff**, **diff**, **verify receipt**, **lineage receipt**, or **assistant slice**.
3. Say explicitly which fields or rules are **shared across seams** and which remain **seam-local**.
4. Do not let an assistant-facing rendering become stronger than the canonical pack it derives from.
5. Do not let a schema/style pass silently become a hosted-platform or Cargo-replacement plan.
6. The broad ladder is unchanged: **Build-State Evidence** remains the strongest broad first build; future stage-0 answers should route through `design/shared-spine-execution-blueprint-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0464)

When a revision touches the archive's **top worthy contributions** and is mainly about **what unlocks what**, it must now keep **unlock leverage** separate from rank, vehicle, proof burden, and bet size.

Minimum discipline:
1. State whether the change is about **importance**, **delivery shape**, **incubation vehicle**, **proof burden**, **bet size**, or **compounding / unlock leverage**.
2. Say explicitly whether each major candidate is being treated as an **upstream substrate unlock**, **evidence generator**, **contract multiplier**, **boundary bridge**, **consumer widener**, or **program seam**.
3. Do not let a later consumer-facing layer silently become “first” merely because it is easier to imagine a product surface.
4. Do not let a narrower upstream milestone silently impersonate a complete public-platform epic.
5. For every new comparative recommendation, prefer saying what reusable artifact or receipt survives if the hosted layer disappears.
6. The broad ladder is unchanged: **Build-State Evidence** remains the strongest one-project answer and now also the clearest first unlock; future unlock-graph answers should route through `design/epic-contribution-compounding-map-2026Q1.md` before rewriting canon.

# Revision operating protocol addendum (rev0463)

When a revision touches the archive's **top worthy contributions**, it must now keep **bet size** separate from rank, vehicle, and proof burden.

Minimum discipline:
1. State whether the change is about **importance**, **delivery shape**, **incubation vehicle**, **proof burden**, or **bet size / funding fit**.
2. Do not imply that the “best” contribution always wants the largest team or the largest institution.
3. For every new comparative recommendation, prefer saying one of these explicitly when relevant:
   - sponsor a maintainer or upstream owner;
   - ship a bootstrap companion build;
   - staff a focused bridge or commons;
   - form a consortium / interoperability program;
   - fund upstream substrate or keystone incubation.
4. Do not let a grant opportunity, sponsor preference, or lab vehicle silently rewrite the broad ladder.
5. Do not let a small team promise coalition-grade acceptance, and do not let a coalition-funded program masquerade as a lightweight plugin.
6. The broad ladder is unchanged: **Build-State Evidence** remains the strongest one-project answer, **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build, and future capital-allocation answers should route through `design/epic-contribution-bet-sizing-map-2026Q1.md` before rewriting canon.

# Revision operating addendum (rev0462)

When a revision sharpens the archive around **what a worthy contribution must actually prove before it deserves widening or support**, it must now answer five questions explicitly:
- what the candidate's **proof family** is,
- what the first **proving ground** is,
- what the first **canonical artifact family** is,
- what **negative or partial states** must be shown,
- and what the **graduation line** is.

Default rule: never let rank alone silently answer proof burden, never let one polished demo count as ecosystem proof, and never let a hosted surface or assistant summary impersonate repeated real-lane evidence.


# Revision operating addendum (rev0461)

When a revision sharpens the archive around **what vehicle a worthy contribution should actually begin in**, it must now answer five questions explicitly:
- what the candidate's **incubation vehicle** is,
- what **staffing or funding posture** that vehicle assumes,
- what the likely **exit path** is,
- what **wrong starting vehicle** should be refused,
- and what stayed merely a **roadmap substrate or stabilization program** instead of being upgraded into a fake public-platform story.

Default rule: never let delivery shape alone silently answer incubation shape, never let a foundation or lab mention impersonate a product plan, and never let one elegant hosted-service instinct count as governance realism.

# Revision operating addendum (rev0460)

When a revision sharpens the archive around **how top worthy contributions should actually be delivered**, it must now answer five questions explicitly:
- what the candidate's **delivery shape** is,
- what the candidate's **owner or steward shape** is,
- what the **first shipped artifact family** is,
- what **proving grounds** it must survive,
- and what **wrong shape** must be refused early.

Default rule: never let rank alone silently answer delivery shape, never let institution aura replace product clarity, and never let one elegant hosted-product instinct count as a delivery plan.


# Revision operating addendum (rev0459)

When a revision sharpens the archive around **comparative priority across several already-worthy candidates**, it must now answer five questions explicitly:
- which candidate is the **broad first build**,
- which candidate is the **second serious build**,
- which candidates are **hidden multipliers**,
- which candidate is merely **urgent** rather than broadly first,
- and which candidate requires a different **steward/ownership shape** such as consortium or program governance.

Default rule: never let one recent advisory, one elegant substrate, one specialist use case, one hosted-product instinct, or one assistant summary silently rewrite all five classes at once.

# Revision operating addendum (rev0458)

When a revision sharpens the archive around **top-band ranking, fold-vs-eliminate decisions, or assistant-operating continuity**, it must now answer six questions explicitly:
- what stayed unchanged in canon,
- what ordering or interpretation changed,
- which sources carried the change,
- which files were touched,
- what remains speculative or only watch-listed,
- and which future refresh should revisit the decision.

Default rule: never let one brainstorm, one elegant summary paragraph, one assistant-memory slice, or one recent source silently count as a full canon rewrite.

Before such a revision rewrites routing files, read `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`.


# Revision operating addendum (rev0457)

When a revision sharpens the archive around **machine-facing Cargo tooling truth**, it must now answer six questions explicitly:
- what is the tooling subject,
- what discovery and scope facts were imported,
- what graph and plan facts were imported,
- what execution or build-state evidence was imported,
- what stability posture or adapter lossiness was recorded,
- and what downstream consumers are still intentionally out of scope.

Default rule: never let one `cargo metadata` dump, one `--message-format=json` stream, one unstable `--unit-graph`, one report log, one `rust-project.json`, one `cargo.targetDir` workaround, or one assistant summary silently count as the whole tooling story.

# Revision operating addendum (rev0456)

When a revision sharpens the archive around **compatibility claims**, it must now answer six questions explicitly:
- what is the claim subject,
- which claim families were in scope,
- which imported-owner facts were used,
- what evidence posture changed,
- what drift or reclassification was recorded,
- and what downstream consumers are still intentionally out of scope.

Default rule: never let one target tier, one docs.rs target list, one `rust-version` field, one semver check, one CI matrix, or one assistant summary silently count as the whole compatibility story.

# Revision operating addendum (rev0455)

When a revision sharpens the archive around **producer-side release continuity**, it must now answer six questions explicitly:
- what is the release subject,
- what source-publication facts were imported,
- what artifact facts were imported,
- what signature/attestation facts were imported,
- what rebuild or inventory facts were imported,
- and what downstream consumers are still intentionally out of scope.

Default rule: never let one crates.io upload, one GitHub Release page, one dist manifest, one signature file, one SBOM precursor, or one rebuild report silently count as the whole producer-side release story.

## rev0454 — observability execution revision rule
Default rule: never let one exporter route, one OTLP profile, one local `fmt` subscriber, one Tokio Console capture, one vendor dashboard, or one assistant summary silently count as the whole observability story.

When a revision claims to improve the archive's **observability logic**, read `design/observability-execution-blueprint-2026Q1.md` and `design/observability-contract-2026Q1.md` before editing canon files.

Such a revision must now say explicitly:
- which observability layer changed;
- whether the revision affected diagnostic identity, signal/profile, activation/route, runtime-diagnostic capability, support/docs, consumer handoff, or only routing/prose;
- which adjacent import seams were intentionally left untouched;
- and whether any exporter-route or runtime-capability caveat changed the archive's practical recommendation posture.

# Revision protocol addendum (rev0453)

## Defect-escalation execution routing rule
If a revision is mainly about **observed failures, minimized repro lineage, routing or duplicate posture, regression-test candidacy, evidence imports, or downstream issue/PR/assistant handoffs**, it should say which layer it is changing:
- **observed-failure truth**,
- **minimization-lineage truth**,
- **routing/dedup truth**,
- **regression-candidate truth**,
- **evidence-import truth**,
- or **consumer handoff**.

Default rule: never let one issue template, one single-file repro, one `cargo-bisect-rustc` transcript, one duplicate guess, one regression-test snippet, or one assistant summary silently count as the whole defect-escalation story.

## Defect-escalation non-collapse rule
When a revision claims to improve the archive's **defect-escalation logic**, read `design/defect-escalation-execution-blueprint-2026Q1.md` and `design/defect-escalation-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which defect-escalation layer changed;
- say whether the revision improved observation truth, minimization lineage, routing/dedup posture, regression-candidate posture, evidence imports, or consumer routing;
- say what stayed `watch` / `defer` / `uncertain-owner` / `possible-duplicate` / `not-regression-ready`;
- and say what conclusions remain prohibited.

# Revision protocol addendum (rev0452)

## Benchmark-evidence execution routing rule
If a revision is mainly about **benchmark subject identity, measurement-lane semantics, collector/configuration posture, baseline posture, comparability verdicts, or bounded performance-review handoffs**, it should say which layer it is changing:
- **subject truth**,
- **measurement-lane truth**,
- **collector/configuration truth**,
- **baseline truth**,
- **verdict/comparability truth**,
- or **consumer handoff**.

Default rule: never let one Criterion run, one Divan table, one nextest import, one callgrind attachment, one hosted benchmark report, one rustc-perf graph, or one CI comment silently count as the whole benchmark-evidence story.

## Benchmark-evidence non-collapse rule
When a revision claims to improve the archive's **benchmark-evidence logic**, read `design/benchmark-evidence-execution-blueprint-2026Q1.md` and `design/benchmark-evidence-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which benchmark-evidence layer changed;
- say whether the revision improved subject truth, lane truth, collector/configuration truth, baseline truth, comparability truth, or consumer routing;
- say what stayed `watch` / `defer` / `lossy` / `not-comparable`;
- and say what conclusions remain prohibited.

# Revision protocol addendum (rev0451)

## Public-API execution routing rule
If a revision is mainly about **public-boundary identity, exposed foreign or public dependencies, structural API diffs, witness-backed semver evidence, bounded verification posture, or downstream release/migration/publish/docs handoffs**, it should say which layer it is changing:
- **subject truth**,
- **exposure truth**,
- **structural-diff truth**,
- **witness/proof truth**,
- **bounded-verification truth**,
- or **consumer handoff**.

Default rule: never let one rustdoc JSON export, one API diff report, one semver lint run, one witness program, one publish check, or one archive summary silently count as the whole public-API story.

## Public-API non-collapse rule
When a revision claims to improve the archive's **public-API logic**, read `design/public-api-execution-blueprint-2026Q1.md` and `design/public-api-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which public-API layer changed;
- say whether the revision improved exposure truth, structural-diff truth, witness/proof truth, bounded-verification posture, or consumer routing;
- say what stayed `watch` / `defer` / `inconclusive` / `unsupported` / `lossy`;
- and say what conclusions remain prohibited.

## Canonical-learning boundary rule (rev0450)
If a revision is about docs, guide books, example validation, compile-guidance surfaces, docs-host posture, editor hints, assistant learning slices, or archive learning summaries, it must say which layer it is changing:
- **subject identity**,
- **canonical-learning lane**,
- **evidence posture**,
- **consumer import**,
- **derived overlay**,
- or **consumer handoff**.

Default rule: never let one docs.rs page, one mdBook render, one doctest run, one diagnostics panel, one archive brief, or one assistant summary silently claim all six layers at once.

# Revision protocol addendum (rev0449)

## Support-envelope execution routing rule
If a revision is mainly about **declared platform/runtime/docs support, runtime-floor truth, host-tool or provisioning posture, observed support evidence, or downstream support handoffs**, it should say which layer it is changing:
- **subject identity**,
- **lane identity**,
- **provisioning/runtime-floor truth**,
- **evidence strength**,
- **support drift**,
- or **consumer handoff**.

Default rule: never let one target tier, one docs.rs target list, one `cargo check` run, one CI matrix entry, one release artifact, or one README platform table silently count as the whole support story.

## Support-envelope non-collapse rule
When a revision claims to improve the archive's **support-envelope logic**, read `design/support-envelope-execution-blueprint-2026Q1.md` and `design/support-envelope-kit.md` before editing canon files.

Minimum answer:
- say which support-envelope layer changed;
- say whether the revision improved lane truth, runtime-floor truth, evidence posture, drift visibility, or consumer routing;
- say what stayed `watch` / `partial` / `declared-only` / `unknown`;
- and say what conclusions remain prohibited.


# Revision protocol addendum (rev0448)

## Toolchain-productization execution routing rule
If a revision is mainly about **toolchain variants, rebuilt std/core families, custom targets, activation/reuse posture, sanitizer or mitigation lanes, or bounded low-level consumer handoffs**, it should say which layer it is changing:
- **provisioning identity**,
- **sysroot/profile identity**,
- **activation / reuse posture**,
- **runtime-analysis / hardening lane**,
- **support-envelope posture**,
- or **consumer handoff**.

Default rule: never let one rustup override, one `build-std` invocation, one custom target JSON, one cache artifact, or one sanitizer CI job silently count as the whole toolchain story.

## Toolchain-productization non-collapse rule
When a revision claims to improve the archive's **toolchain-productization logic**, read `design/toolchain-productization-execution-blueprint-2026Q1.md` and `design/toolchain-productization-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which toolchain-product layer changed;
- say whether the revision improved provisioning truth, sysroot truth, activation truth, runtime-lane truth, support-envelope truth, or consumer routing;
- say what stayed `watch` / `defer` / `unstable` / `out-of-scope`;
- and say what conclusions remain prohibited.


# Revision-operating addendum (rev0447)

When a revision is mainly about **what a reviewable mutation / selection / verification seam should actually ship**, prefer an **execution-blueprint deepening** before a fresh frontier promotion.

Minimum rule:
- say why current edit producers are still fragmented in daily practice rather than only in theory;
- say what primary contribution shape now fits the seam best;
- say what core truth classes must stay separate;
- say what first serious producer/consumer proving lanes would demonstrate it honestly;
- and say which attractive implementation stories should be refused.

Default interpretation:
- do not let `cargo fix`, migration lore, IDE assists, or assistant patches silently define the whole seam;
- require one answer for subject, provenance, selection, application, verification, and handoff truth;
- and treat future agent/CI workflows as downstream consumers of the edit boundary, not its replacement.

# Revision protocol addendum (rev0446)

## Publisher/source-identity execution routing rule
If a revision is mainly about **package publication identity, family/namespace claims, publish authority, source-route posture, source-hint boundaries, or downstream handoffs**, it should say which layer it is changing:
- **subject truth**,
- **claim truth**,
- **publisher-authority truth**,
- **source-route truth**,
- **source-hint / provenance-boundary truth**,
- or **consumer handoff**.

Default rule: never let one owner list, one trusted-publisher setting, one namespace claim, one alternate-registry entry, one replacement-source config, one repository link, or one VCS hint silently count as the whole publisher/source-identity story.

## Publisher/source-identity non-collapse rule
When a revision claims to improve the archive's **publisher/source-identity logic**, read `design/publisher-source-identity-execution-blueprint-2026Q1.md` and `design/publisher-source-identity-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which publisher/source-identity layer changed;
- say whether the revision improved claim truth, publisher-authority truth, route truth, provenance-boundary truth, or consumer routing;
- say what stayed `watch` / `defer` / `lossy` / `unverified`;
- and say what conclusions remain prohibited.

# Revision protocol addendum (rev0445)

## Workspace-environment execution routing rule
If a revision is mainly about **workspace discovery, declared environment intent, realization across host/devcontainer/Nix/CI/remote lanes, observed environment drift, or bounded environment handoffs**, it should say which layer it is changing:
- **subject/discovery truth**,
- **declared-intent truth**,
- **realization truth**,
- **secret/credential posture**,
- **observation/drift truth**,
- or **consumer handoff**.

Default rule: never let one `rust-toolchain.toml`, one `.cargo/config.toml`, one rust-analyzer override command, one devcontainer, one flake, one CI image, or one support transcript silently count as the whole workspace-environment story.

## Workspace-environment non-collapse rule
When a revision claims to improve the archive's **workspace-environment logic**, read `design/workspace-environment-execution-blueprint-2026Q1.md` and `design/workspace-environment-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which workspace-environment layer changed;
- say whether the revision improved subject/discovery truth, declared intent, realization posture, secret posture, observation truth, or consumer routing;
- say what stayed `watch` / `defer` / `lossy` / `redacted`;
- and say what conclusions remain prohibited.

# Revision protocol addendum (rev0444)

## Distribution-contract execution routing rule
If a revision is mainly about **delivery, acquisition, fallback, verification, installed ownership, or consumer-side handoffs**, it should say which layer it is changing:
- **release-import truth**,
- **route/catalog truth**,
- **selection/fallback truth**,
- **verification truth**,
- **installed-ownership truth**,
- or **consumer handoff**.

Default rule: never let one `cargo install` run, one prebuilt download, one mirror configuration, one package-manager import, one rustup path, or one support transcript silently count as the whole distribution story.

## Distribution-contract non-collapse rule
When a revision claims to improve the archive's **distribution-contract logic**, read `design/distribution-contract-execution-blueprint-2026Q1.md` and `design/distribution-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which distribution layer changed;
- say whether the revision improved route truth, selection/fallback truth, verification posture, ownership truth, or consumer routing;
- say what stayed `watch` / `defer` / `delegated` / `lossy`;
- and say what conclusions remain prohibited.

# Revision protocol addendum (rev0443)

## Artifact-contract execution routing rule
If a revision is mainly about **Cargo final outputs, artifact staging/uplift, sidecar attachment, or downstream artifact handoffs**, it should say which layer it is changing:
- **selected-subject identity**,
- **evidence-path truth**,
- **final-artifact identity**,
- **origin/staging truth**,
- **sidecar attachment**,
- or **consumer handoff**.

Default rule: never let one `target/` walk, one `--message-format=json` stream, one `--artifact-dir` copy, one build-script output directory, one SBOM precursor file, or one release manifest silently count as the whole artifact story.

## Artifact-contract non-collapse rule
When a revision claims to improve the archive's **Cargo artifact-contract logic**, read `design/cargo-artifact-contract-execution-blueprint-2026Q1.md` and `design/cargo-artifact-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which artifact layer changed;
- say whether the revision improved selected-subject truth, artifact identity, origin/staging truth, sidecar truth, or consumer routing;
- say what stayed `watch` / `defer` / `lossy` / `unstable`;
- and say what conclusions remain prohibited.

# Revision protocol addendum (rev0442)

## Safety-critical-readiness execution routing rule
If a revision is mainly about **safety-critical adoption, qualification posture, target readiness, dependency lifecycle, or mixed-language boundary posture**, it should say which layer it is changing:
- **critical-slice identity**,
- **authority / requirement profile**,
- **qualified-scope truth**,
- **target/runtime readiness**,
- **dependency-lifecycle posture**,
- **interface / interop posture**,
- or **consumer handoff**.

Default rule: never let one target checklist, one vendor qualification manual, one evidence pack, one async-runtime note, or one FFI success story silently count as the whole safety-readiness story.

## Safety-critical-readiness non-collapse rule
When a revision claims to improve the archive's **safety-critical readiness commons logic**, read `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md` and `design/safety-critical-assurance-contract-2026Q1.md` before editing canon files.

Minimum answer:
- say which safety-readiness layer changed;
- say whether the revision improved qualified-scope truth, target/runtime posture, dependency posture, interface posture, or consumer routing;
- say what stayed `watch` / `defer` / `out-of-scope`;
- and say what conclusions remain prohibited.

# Revision protocol addendum (rev0441)

## Async-commons execution routing rule
If a revision is mainly about **async runtime plurality, partial portability, capability truth, or runtime/environment adapter posture**, it should say which layer it is changing:
- **lane identity**,
- **capability profile**,
- **common-surface claim**,
- **adapter/bridge truth**,
- **environment contrast**,
- or **consumer handoff**.

Default rule: never let one runtime tutorial, one adapter crate, one language stabilization, one benchmark anecdote, or one “runtime agnostic” README silently count as the whole async story.

## Async-commons non-collapse rule
When a revision claims to improve the archive's **async capability commons logic**, read `design/async-capability-commons-execution-blueprint-2026Q1.md` and `design/async-commons-lane-map.md` before editing canon files.

Minimum answer:
- say which async lane or lanes changed;
- say whether the revision improved capability truth, adapter truth, or consumer routing;
- say what stayed `watch` / `defer`;
- and say what conclusions remain prohibited.

## Revision operating addendum (rev0440)

When a revision changes the archive's **maintainer reality / keystone stewardship execution story**, it must now answer four questions explicitly:
- did the top-level execution blueprint change,
- did the maintenance-reality or keystone stack assumptions change,
- did the working-set / amnesia-resistor routing change,
- and did the revision keep lifecycle, operations, keystone, institutional-support, continuity-risk, and consumer truth visibly separate?

Minimum rule:
- if the repo materially changes what maintainer/stewardship work should ship, update `design/maintainer-reality-keystone-stewardship-execution-blueprint-2026Q1.md`, at least one of `design/maintenance-reality-stack.md` or `design/keystone-stewardship-stack.md` if their assumptions moved, and the relevant top-level routing files in the same revision;
- if none of those changed, say so rather than silently leaving the stewardship execution story stale.

Do not let a revision that only changes rhetoric, only changes a pilot, or only changes consumer summaries silently redefine the stewardship contribution.
The blueprint, stacks, and routing rules must move together when the program-shaped execution answer moves.

# Revision-operating addendum (rev0439)

When a revision is mainly about **what an under-ranked but strategically important missing middle should actually ship**, prefer an **execution-blueprint deepening** before a promotion.

Minimum rule:
- say why the seam is still missing in daily practice rather than only in theory;
- say what primary contribution shape now fits it best;
- say what core truth classes must stay separate;
- say what first serious pilot lanes would prove it honestly;
- and say which attractive implementation stories should be refused.

Default interpretation:
- a missing-middle blueprint is an execution-design layer for the canon, not a frontier by itself;
- do not let “important in the survey” silently collapse into “one debugger/framework/service should own it”;
- and do not let build evidence, debugger evidence, acceptance evidence, and consumer summaries silently impersonate one another because the workflow pain is emotionally vivid.

# Revision-operating addendum (rev0438)

When a revision is mainly about **what ideal Rust is still missing, which candidate contributions deserve top billing, and which attractive directions should now be folded or killed**, prefer an **ideal-Rust synthesis deepening** before a frontier promotion.

Minimum rule:
- say which candidates are being treated as **build-now epics**;
- say which candidates are being treated as **substrate multipliers**;
- say which candidates are honestly **specialist/program-shaped** rather than one-crate-shaped;
- say which candidates are being **folded, downgraded, or eliminated**;
- and say whether the broad ladder or active frontier actually changed.

Default interpretation:
- ideal-Rust synthesis is a territory-mapping and anti-category-error layer for the canon, not a frontier by itself;
- do not let a ranking pass silently confuse “important” with “crate-shaped”;
- and do not let a fashionable idea survive just because it sounds large if the archive cannot say what truth it leaves behind, what artifact family makes it real, and what it explicitly refuses to own.

# Revision-operating addendum (rev0437)

When a revision is mainly about **what class of deliverable a worthy seam should become**, prefer a **contribution-shape deepening** before a promotion.

Minimum rule:
- say which shape is primary **now**;
- say what artifacts make that shape real;
- say what adjacent shape the proposal is most likely to be confused with;
- say why the wrong shape would distort the seam;
- and if the shape model changed materially, update the design note, the protocol, the morphology corpus, and the checker together.

Default interpretation:
- contribution shapes are a maintenance and execution-design layer for the canon, not a new frontier;
- one seam may legitimately involve more than one shape over time, but the first serious step should still be named;
- and do not let a local report command, a hosted service, a corpus, a bridge, or a program all silently impersonate one another because the seam sounds important.

## Source-atlas routing rule (rev0436)
If a revision is mainly about **which upstream source families should support recurring canon claims, what caveats must travel with those sources, and whether the archive is mixing authority lanes dishonestly**, it must say which layer it is changing:
- **source card**,
- **authority lane**,
- **claim-family fit**,
- **known caveat**,
- **refresh signal**,
- or **repo hygiene only**.

Default rule: never let one fresh blog post, one survey snapshot, one goals page, one reference page, or one service-doc page silently count as the whole evidentiary basis for a broad canon claim without naming what kind of claim that source is actually fit to support.

## Source atlas rule
When a revision claims to improve the archive's **recurring-source discipline**, it should leave behind or refresh assets that cover source identity, authority lane, preferred claim classes, known caveats, refresh signals, and linked canon assets.

Use `meta/SOURCE_ATLAS_PROTOCOL.md` as the minimum template.

## Hypothesis-ledger routing rule (rev0435)
If a revision is mainly about **which repeated strategic claims in the canon are still live, what evidence currently keeps them plausible, and what should visibly narrow or break them**, it must say which layer it is changing:
- **claim statement**,
- **support lane**,
- **downgrade trigger**,
- **falsifier**,
- **review horizon**,
- or **repo hygiene only**.

Default rule: never let one repeated conclusion, one vivid citation, one successful pilot, or one maintainer habit silently count as an immortal canon claim without naming what would narrow it or falsify it.

## Hypothesis ledger rule
When a revision claims to improve the archive's **live-claim discipline**, it should leave behind or refresh assets that cover claim identity and class, explicit statement, support lanes or sources, downgrade triggers, falsifiers, review horizon, and linked canon assets.

Use `meta/HYPOTHESIS_LEDGER_PROTOCOL.md` as the minimum template.

## Anchor-corpus routing rule (rev0434)
If a revision is mainly about **what representative case profiles a pilot exercised once it already named a proving-ground scenario**, it must say which layer it is changing:
- **scenario coverage**,
- **anchor profile**,
- **hold-constant discipline**,
- **allowed variation**,
- or **repo hygiene only**.

Default rule: never let one attractive private demo, one benchmark anecdote, one release smoke test, or one docs walkthrough silently count as a representative case without naming the anchor profile it satisfied.

## Anchor corpus rule
When a revision claims to improve the archive's **representative-case discipline**, it should leave behind or refresh assets that cover:
- anchor identity and scenario bindings;
- representative traits;
- hold-constant vs allowed-variation guidance;
- minimum artifacts;
- and explicit non-claims.

Use `meta/ANCHOR_CORPUS_PROTOCOL.md` as the minimum template.

# Revision operating addendum (rev0433)

When a revision changes the archive's **shared proving-grounds matrix, scenario-card minimums, or proving-grounds checker duties**, it must now answer four questions explicitly:
- did the proving-grounds note change,
- did the proving-grounds protocol change,
- did the shared scenario corpus change,
- and did the proving-grounds checker still pass after the revision?

Minimum rule:
- if shared scenario fields, required class coverage, or proving-ground expectations changed materially, update `design/portfolio-proving-grounds-2026Q1.md`, `meta/PROVING_GROUNDS_PROTOCOL.md`, `proofgrounds/portfolio-scenario-matrix-v0/scenarios.json`, and `tools/check_proving_ground_matrix.py` in the same revision;
- if none of those changed, say so rather than silently leaving the matrix stale.

Do not let a revision that only edits prose, only edits the matrix, or only edits the checker silently redefine the proving grounds.
The note, protocol, matrix, and checker must move together when the shared pilot terrain moves.

# Revision operating addendum (rev0432)

When a revision changes the archive's **required doctor checks, required doctor files, or doctor receipt shape**, it must now answer four questions explicitly:
- did the doctor protocol change,
- did the doctor tool change,
- did the last-run receipt change,
- and did the doctor still pass after the revision?

Minimum rule:
- if required doctor files, required commands, or receipt fields changed materially, update `design/portfolio-archive-doctor-2026Q1.md`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`, `tools/archive_doctor.py`, and `meta/ARCHIVE_DOCTOR_LAST_RUN.json` in the same revision;
- if none of those changed, say so rather than silently leaving the doctor stale.

Do not let a revision that only edits prose, only edits the tool, or only refreshes the receipt silently redefine the maintenance loop.
The note, protocol, tool, and receipt must move together when the doctor contract moves.

# Revision operating addendum (rev0431)

When a revision changes the archive's **shared portfolio-envelope grammar**, it must now answer four questions explicitly:
- did a hard honesty rule change,
- did a positive specimen change,
- did a negative fixture change,
- and did `python tools/check_portfolio_envelope_contract.py` still pass?

Minimum rule:
- if shared fields, role minimums, lineage discipline, or escalation posture changed materially, update `design/portfolio-conformance-validation-2026Q1.md`, `meta/PORTFOLIO_CONFORMANCE_PROTOCOL.md`, and at least one affected specimen or negative fixture in the same revision;
- if none of those changed, say so rather than silently leaving the checker untouched.

Do not let a revision that only updates prose, only updates examples, or only updates the checker silently redefine the contract.
The checker, specimens, and protocol must move together when hard rules move.

# Revision-operating addendum (rev0430)

When a revision changes the archive's **shared envelope grammar, routed-brief posture, verify-receipt posture, or lineage rules**, it must now ask whether the specimen corpus changed too.

Minimum rule:
- if the change would make a current specimen teach the wrong habit, refresh that specimen in the same revision;
- if no specimen changed, say why;
- and if a new shared role becomes important, prefer adding one small specimen before adding another prose-only note.

Default interpretation:
- **reference specimens** are a maintenance layer for the canon, not a new strategic frontier;
- keep the specimen corpus small and role-complete before making it seam-complete;
- and do not let one assistant-authored example silently become the repo's de facto grammar without entering `specimens/` and `meta/SPECIMEN_CORPUS_PROTOCOL.md`.

## New consumer-routing rule (rev0429)
If a revision is mainly about the archive's **briefs, hints, CI summaries, release/security summaries, editor slices, or assistant-facing renderings**, prefer a **consumer-routing deepening** before a promotion or re-ranking.

Minimum routing answer:
- say which **consumer class** the view is for;
- say which **decisions** it may support;
- say what **authority floor** it preserves;
- say what **lossiness budget** it is using;
- say what **conclusions are prohibited**;
- and end with an explicit **escalation target** back to the canonical pack or stronger receipt.

Default rule:
- do **not** let one CI summary, one editor hint, one release dashboard, one security brief, or one assistant summary silently impersonate the canonical artifact;
- do **not** let one consumer-friendly slice silently expand the decisions it is allowed to drive;
- prefer **route honestly and escalate** before **flatten everything into one universal summary**.

Read with:
- `design/portfolio-consumer-routing-2026Q1.md`
- `meta/CONSUMER_ROUTING_PROTOCOL.md`


## New renewal rule (rev0428)
If a revision is mainly about the archive's **freshness, drift, or current-source credibility**, prefer a **renewal deepening** before a promotion or re-ranking.

Minimum renewal answer:
- say which claim class changed: structural / substrate / service-behavior / security-incident / ecosystem-tooling;
- say which authority lane was re-checked;
- say whether the note was hot / warm / cool / cold;
- say what triggered the review;
- and end with an explicit verdict of **confirmed / narrowed / degraded / superseded / retired**.

Default rule:
- do **not** let one stale survey, one old goals page, one hosted-service assumption, one security advisory, or one assistant summary keep impersonating live truth;
- do **not** let one fresh source silently rewrite the broad ladder either;
- prefer **renew**, **narrow**, or **degrade** before **re-rank** when the broad seam judgment still holds.

Read with:
- `design/portfolio-evidence-renewal-2026Q1.md`
- `meta/EVIDENCE_RENEWAL_PROTOCOL.md`
- `meta/CANONICAL_RENEWAL_QUEUE.md`


# Revision protocol addendum (rev0427)

## Pilot-proof routing rule
If a revision is mainly about **how a worthy seam was piloted, whether the pilot worked, or whether a stage should now widen**, it must say which layer it is changing:
- **lane exercised**,
- **artifacts emitted**,
- **downstream decisions exercised**,
- **residue / unsupported states**,
- **steward cost**,
- or **explicit verdict**.

Default rule: never let one benchmark anecdote, one dashboard, one happy-path demo, one agentic workflow, or one local speedup silently count as a successful pilot in general.

## Pilot scorecard rule
When a revision claims that a pilot proved something important, it should leave behind a card or note that covers:
- pilot identity and seam;
- lane statement and baseline;
- imports and assumptions;
- artifacts emitted;
- decisions exercised;
- outcome deltas;
- steward cost;
- and an explicit **graduate / deepen / fold / delay / kill** verdict.

Use `meta/PILOT_SCORECARD_PROTOCOL.md` as the minimum template.


# Revision operating-protocol addendum (rev0426)

When a revision claims to improve the archive's **worthy-contribution selection logic**, **candidate ranking discipline**, or **proposal triage**, read `design/portfolio-selection-rubric-2026Q1.md` and `meta/CANDIDATE_TRIAGE_PROTOCOL.md` before editing canon files.

Default rule:
- declare explicitly whether the revision changed **ranking**, **selection rubric**, **candidate-card protocol**, **fold/kill criteria**, or only **repo hygiene**;
- if candidate-selection rules changed, update `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, and `meta/AMNESIA_RESISTORS.md` together;
- do not promote a new candidate unless it names ranking class, seam sentence, artifact family, pilot lane, imports, steward story, and fold/kill triggers;
- and prefer **deepen** or **fold** over **promote** when the new evidence sharpens an existing seam more than it creates a new one.

# Revision operating-protocol addendum (rev0425)

When a revision claims to improve the archive's **portfolio build order**, **funder answer**, or **staffing/maintenance posture**, read `design/portfolio-execution-sequencing-2026Q1.md` before editing canon files.

Default rule:
- declare explicitly whether the revision changed **ranking**, **staging order**, **stage gates**, **stewardship model**, or only **repo hygiene**;
- if staging changed, update `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, and `meta/AMNESIA_RESISTORS.md` together;
- say which stage the revision belongs to: **shared spine**, **evidence spine**, **boundary bridge**, or **consumer/frontier widening**;
- and do not let launch excitement silently outrun maintainer/steward capacity.

# Revision operating-protocol addendum (rev0424)

When a revision touches **more than one execution blueprint** or claims to improve the archive's multi-project answer, read `design/portfolio-artifact-conventions-2026Q1.md` before editing canon files.

Default rule:
- declare explicitly whether the revision changed **ranking**, **shared grammar**, **seam payload design**, or only **repo hygiene**;
- if shared grammar changed, update `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, and `meta/AMNESIA_RESISTORS.md` together;
- and do not let a shared envelope / lineage receipt / validator silently rewrite seam-specific payload semantics.

# Revision protocol addendum (rev0423)

When a revision is really about the archive's **active specialist frontier** rather than a new frontier promotion, say explicitly that the revision is **deepening** and route execution questions to `design/native-edge-execution-blueprint-2026Q1.md`.

Default interpretation until stronger evidence arrives:
- **Native Edge Contract** remains the active specialist frontier, not a new overall #1;
- the preferred execution shape is a **portable native-edge reference layer** above imported boundary, provider/link, context, and handoff evidence;
- future revisions must keep **subject**, **boundary**, **provider/link**, **host-vs-target/toolchain context**, **foreign-build handoff**, and **brief/consumer truth** visibly separate;
- do not silently collapse the seam into another binding generator, another `-sys` helper empire, another universal bridge, or another assistant oracle.

# Revision protocol addendum (rev0422)

When a revision is really about the archive's **anti-tacit-knowledge / recommendation frontier** rather than a new frontier promotion, say explicitly that the revision is **deepening** and route execution questions to `design/adoption-navigation-execution-blueprint-2026Q1.md`.

Default interpretation until stronger evidence arrives:
- **Adoption Navigation Contract** is the strongest anti-tacit-knowledge answer, not a new overall #1;
- the preferred execution shape is a **portable recommendation-review layer** above defaults, canon, evidence, and local-fit imports;
- future revisions must keep **question**, **lane**, **canon**, **evidence**, **local-fit**, and **handoff** visibly separate;
- do not silently collapse the seam into another curated website, another score empire, or another assistant oracle.


# Revision protocol addendum (rev0421)

When a revision is really about the archive's **release / upgrade portfolio seam** rather than a new frontier promotion, say explicitly that the revision is **deepening** and route execution questions to `design/migration-public-api-execution-blueprint-2026Q1.md`.

Default interpretation until stronger evidence arrives:
- **Migration/Public API** is a portfolio seam, not a new frontier;
- the preferred execution shape is a **portable public-boundary + upgrade-program bridge** above imported Public API and Migration Truth evidence;
- future revisions must keep **subject**, **proof**, **intent**, **application**, **verification/outcome**, and **consumer handoff** visibly separate;
- do not silently collapse the seam into another semver checker, another fixer wrapper, or another release checklist.

## Operational-seam blueprint rule (rev0420)
If a revision is mainly about the archive's **operationally urgent seam**, prefer a **deepening blueprint** before a fresh promotion.

Default rule:
- keep **one-project winner**, **active specialist frontier**, **operational seam**, and **hidden multiplier** visibly separate;
- if the seam is **Package Intake Gateway**, sharpen **route**, **payload**, **staging / extraction**, **resolution**, and **handoff** truth instead of widening into a generic supply-chain empire;
- and say explicitly whether the revision is about **ingress review** or one of its adjacent layers: **package admission**, **dependency review**, **compile-time execution authority**, **consumer install**, or **SBOM / incident response**.

## Hidden-multiplier deepening rule (rev0419)
If a revision is mainly about the archive's current **hidden multiplier**, prefer adding or refreshing an **execution blueprint** before promoting another seam.

Default rule:
- keep the broad ranking intact unless the new evidence really defeats it;
- make the blueprint explicit about **artifact families, commands, lane order, query budgets, consumer handoffs, and anti-goals**;
- keep **one-project winner**, **active specialist frontier**, and **operational urgency seam** separate from the hidden multiplier;
- and do not let a sharper substrate plan silently become a universal index, verdict engine, or assistant platform.


## One-project-winner deepening rule (rev0418)
If a revision is mainly about the archive's current **one-project winner**, prefer adding or refreshing an **execution blueprint** before promoting another seam.

Default rule:
- keep the broad ranking intact unless the new evidence really defeats it;
- make the blueprint explicit about **artifact families, commands, pilot lanes, authority posture, and anti-goals**;
- keep **operational urgency** and **active specialist frontier** separate from the one-project winner;
- and do not let a sharper execution plan silently become another platform empire.

## Worthy-contribution routing rule
If a revision is mainly answering **“what should we actually build or fund next?”**, it must separate:
- **one-project winner**,
- **multi-project portfolio answer**,
- **active specialist frontier**,
- **operationally urgent seam**,
- and **hidden multiplier / enabling substrate**.

Default rule:
- read `design/strategic-territory-map-2026Q1.md` and `design/worthy-contribution-shortlist-2026Q1.md` before mutating rankings;
- do **not** let one active frontier silently become the one-project winner;
- do **not** let one operational scare silently become the whole portfolio answer;
- and do **not** let one hidden multiplier silently flatten adjacent seams that should stay explicit.

## Portfolio-synthesis rule
If a revision is mainly about **archive-wide ranking, portfolio pruning, or “what should Rust build next?”**, it must say explicitly whether it is:
- **promotion**,
- **deepening**,
- **synthesis with no new promotion**,
- or **hygiene**.

Default rule:
- do **not** let one active frontier silently become the whole portfolio answer;
- do **not** let one exciting source silently rewrite the broad ladder;
- keep **broad build priority**, **specialist frontier priority**, **hidden multiplier priority**, **elimination/folding decisions**, and **current active frontier** visibly separate;
- and prefer writing one explicit synthesis note before mutating multiple top-band rankings.

## Native-edge boundary rule
If a revision is about Rust/C/C++ interop, `bindgen`, `cbindgen`, CXX, `autocxx`, `-sys` crates, provider selection, Corrosion/CMake handoff, or foreign-build integration, it must say which layer it is changing:
- **native-edge subject truth**,
- **boundary truth**,
- **provider / link truth**,
- **host-vs-target / toolchain / external-build context**,
- or **consumer handoff**.

Default rule: never let one generated header, one `bindgen` run, one CXX bridge module, one provider lock, one CMake import, or one support/audit summary silently claim all five layers at once.


## Public-API boundary rule
If a revision is about library evolution, semver checks, public/private dependencies, rustdoc JSON release evidence, public-surface diffs, witness-based compatibility checking, or publish-time API gates, it must say which layer it is changing:
- **public-boundary subject truth**,
- **exposure truth**,
- **structural-diff truth**,
- **witness / type-proof truth**,
- **bounded verification truth**,
- or **consumer handoff**.

Default rule: never let one rustdoc JSON export, one `cargo-public-api` diff, one semver lint run, one witness compile, one MSRV job, or one release note silently claim all six layers at once.


## Migration boundary rule
If a revision is about edition upgrades, `cargo fix`, dependency upgrades, `rust-version` ratchets, API-sensitive migrations, docs/support validation after change, or assistant-mediated upgrade help, it must say which layer it is changing:
- **source-state truth**,
- **destination-intent truth**,
- **mechanical-edit truth**,
- **compatibility / support / docs / downstream import truth**,
- **run / outcome truth**,
- or **consumer handoff**.

Default rule: never let one `cargo fix` run, one dependency-bump PR, one semver report, one docs check, or one green CI pass silently claim all six layers at once.

## Defect-escalation boundary rule
If a revision is about bug reports, reproducers, issue-routing, duplicate search, MCVEs, bisections, regression candidates, or assistant-mediated filing, it must say which layer it is changing:
- **observation / session truth**,
- **minimization-lineage truth**,
- **routing / dedup posture**,
- **regression-candidate posture**,
- or **consumer handoff**.

Default rule: never let one Markdown snippet, one MCVE, one label set, one duplicate guess, or one assistant-generated issue body silently claim all five layers at once.

## Adoption-navigation boundary rule
If a revision is about recommendations, stack choice, starter sets, curated lanes, onboarding guidance, default cards, or assistant-ready ecosystem guidance, it must say which layer it is changing:
- **question / decision surface**,
- **candidate lanes / candidate set**,
- **canonical references**,
- **imported evidence**,
- **local-fit grounding**,
- **brief / handoff**,
- or the adjacent **reviewable defaults / renewal receipts** layer.

Default rule: never let one curated site, one docs page, one internal approved-stack memo, one starter template, one local prototype, or one assistant summary silently claim all seven layers at once.

## Publisher/source identity boundary rule
If a revision is about registry identity, owners, team owners, trusted publishers, namespaces, alternate registries, source replacement, mirrors, or provenance hints, it must say which layer it is changing:
- **claim / family / namespace posture**,
- **publisher authority posture**,
- **source route posture**,
- **source-hint / provenance-boundary posture**,
- or **consumer handoff**.

Default rule: never let one owner list, one trusted-publisher record, one namespace debate, one alternate-registry entry, one replacement-source setup, or one VCS hint silently claim all five layers at once.


## Observability boundary rule
If a revision is about tracing, logging, metrics, OpenTelemetry, runtime diagnostics, telemetry activation, exporter posture, or observability support claims, it must say which layer it is changing:
- **diagnostic identity**,
- **signal / profile**,
- **activation / route**,
- **support / docs**,
- **imported evidence**,
- or **consumer handoff**.

Default rule: never let one exporter choice, one collector config, one dashboard, one runtime probe, or one support transcript silently claim all six layers at once.

## Safety-critical assurance boundary rule
If a revision is about safety-critical evidence, assurance, coverage criteria, unsafe-contract citations, lint/coding-standard posture, proofs, or certification-facing handoffs, it must say which layer it is changing:
- **critical slice / subject**,
- **authority source / citation lane**,
- **requirement profile / rule set**,
- **evidence-lane import / comparability**,
- **waiver / unsupported residue**,
- or **consumer handoff**.

Default rule: never let one lint run, one coverage percentage, one proof backend, one FLS snapshot, one unsafe-doc citation set, or one audit summary silently claim all six layers at once.

## Harness/testing boundary rule
If a revision is about tests, benches, doctests, runners, or CI-visible test tooling, it must say which layer it is changing:
- **subject discovery**,
- **capability declaration**,
- **harness semantics**,
- **runner / adapter behavior**,
- **run-result evidence**,
- or **specialized attachments / policy consumers**.

Default rule: never let one runner, one JSON export, one JUnit bridge, or one CI wrapper silently claim all six layers at once.

## Semantic-context boundary rule
If a revision is about cross-crate analysis, semantic caching, docs.rs imports, compiler-backed semantic exports, fix-context capture, or assistant context, it must say which layer it is changing:
- **subject identity**,
- **authority lane**,
- **merge / completeness**,
- **query / result**,
- **consumer slice**,
- or **comparison / handoff**.

Default rule: never let one docs.rs fetch, one local rustdoc JSON build, one `cargo metadata` approximation, one `rmeta` merge, one StableMIR export, or one assistant prompt silently claim all six layers at once.


## Workspace-environment boundary rule
If a revision is about setup, onboarding, dev environments, CI parity, editor parity, or agent-safe workspace handoffs, it must say which layer it is changing:
- **subject / discovery**,
- **declared intent / requirements**,
- **realization substrate**,
- **secret / credential posture**,
- **observation / drift**,
- or **consumer handoff**.

Default rule: never let one new environment family silently claim all six layers at once, and never let Cargo build interop or final-artifact surfaces impersonate the workspace-environment boundary.

## Build-interop boundary rule
If a revision is about Cargo in editors, wrappers, CI, or larger build systems, it must say which layer it is changing:
- **workspace discovery**,
- **workspace / unit graph**,
- **build intent / plan**,
- **execution events**,
- **adapter projection / handoff**,
- or the adjacent **final-artifact contract**.

Default rule: never let one new interop family silently claim all six layers at once, and never let the artifact boundary impersonate the graph/plan/event boundary.

## Artifact/plumbing boundary rule
If a revision is about build outputs, Cargo plumbing, build-system integration, or final-artifact handoffs, it must say which layer it is changing:
- **build subject / phase boundary**,
- **final artifact identity**,
- **origin / staging / copy behavior**,
- **artifact-sidecar attachment**,
- or **downstream handoff composition**.

Default rule: never let one new artifact family silently claim all five layers at once.

## Proc-macro transition boundary rule
If a revision is about macros, reflection, or compile-time automation, it must say which layer it is changing:
- **macro workflow / inventory-cost-debug**,
- **compile-time execution authority**,
- **transition-target comparison**,
- or **migration-planning / consumer handoff**.

Default rule: never let one new artifact family silently claim all four layers at once.

## Compatibility-claim boundary rule
If a revision is about support, compatibility, or long-lived support posture, it must say which layer it is changing:
- **support envelope**,
- **debugger tuple / debuggability import**,
- **acceptance surface**,
- or **compatibility-claim composition / consumer summary**.

Default rule: never let one new artifact family silently claim all four layers at once.

## Supply-chain boundary rule
If a revision is about supply-chain, security, or package ingress, it must say which layer it is changing:
- **publication admission**,
- **package intake**,
- **dependency review**,
- **compile-time execution authority**,
- or **consumer install / lifecycle**.

Default rule: never let one new artifact family silently claim all five layers at once.

## Delivery / acquisition boundary rule
If a revision is about installers, prebuilt/source delivery routes, mirrors, package-manager imports, release-host handoffs, or consumer acquisition, it must say which layer it is changing:
- **release import**,
- **catalog / route visibility**,
- **selection / fallback**,
- **verification**,
- **installed ownership**,
- or **consumer handoff**.

Default rule: never let one `cargo install` run, one binstall fetch, one cargo-dist installer, one mirror URL, or one support transcript silently claim all six layers at once.

## Edit / mutation boundary rule
If a revision is about fixes, refactors, migrations, code actions, or assistant/bot patching, it must say which layer it is changing:
- **subject/context**,
- **candidate provenance**,
- **selection / ordering**,
- **application result**,
- **verification**,
- or **consumer handoff**.

Default rule: never let one `cargo fix` run, one editor action, one migration pass, or one assistant patch silently claim all six layers at once.

## Composition-promotion rule
If a revision promotes a **composition seam** (for example a bundle that sits above existing stacks), it must say which of these is true:
- the seam rose in the **overall ecosystem/build ladder**;
- or it merely became the next **bundle-shaping / frontier-composition** move while the broader ladder stayed intact.

Default rule: never let “next seam to shape” silently become “new overall #1 need.”

## Ladder-refresh rule
If a revision’s primary class is **ladder refresh**, it must record all four of these somewhere visible:
- what rose;
- what stayed high but did **not** become the next lane;
- what was explicitly **not** promoted;
- and whether **broad ecosystem priority** differs from **next public-lane candidacy**.

Default rule: if a ladder refresh cannot name at least one “not promoted yet” candidate and why it stayed below the cut line, it is probably just mood-setting prose rather than useful frontier discipline.

# Meta: Revision Operating Protocol

## Purpose
This file exists to keep future archive revisions legible, cumulative, and less vulnerable to LLM drift.
The archive is now large enough that a revision can easily add value in one place while silently increasing confusion elsewhere.
This protocol is the minimum operating loop for repo-shaping edits.

## Required first decision
Every serious revision should classify itself before adding files.
Choose one primary class:
1. **bundle shaping** — turn an existing stack family into a concrete bundle or epic candidate;
2. **stack / leaf deepening** — sharpen one existing seam or kit without changing repo-wide ranking;
3. **ladder refresh** — re-rank needs, build priority, or frontier order;
4. **synthesis / merge / delete** — reduce sprawl by merging adjacent notes or eliminating weaker paths;
5. **hygiene / meta only** — improve archive operation without promoting a new Rust ecosystem contribution.

Default rule: prefer one primary class per revision.
A revision may do minor supporting work in other classes, but it should not pretend to do all five at once.

## Promotion checklist
If a revision promotes a candidate into a new bundle, epic, or frontier slot, it should record all of the following somewhere visible:
- **what is being promoted**;
- **why now**;
- **what lower layers it composes**;
- **what the MVP proves**;
- **what not to build**;
- **which nearby candidates were considered and not promoted**.

If those six items are not visible, the archive is probably accumulating prestige language instead of a buildable frontier.

## Canonical update set
When a revision changes the repo’s shape, update all of these unless there is a deliberate reason not to:
- `INDEX.md`
- `PRIORITIES.md`
- `RESEARCH_LOG.md`
- `STRATEGIC_FRONTIER.md`
- `AGENTS.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/AMNESIA_RESISTORS.md`
- any changed design / proposal files
- mirrored copies under `archive/`
- `meta/ARCHIVE_MANIFEST.md`

Default rule: if the archive’s frontier moved, the mirror and manifest must move too.

## Evidence rules
- Prefer dated official sources when they exist.
- Record the strongest sources in the changed design/proposal files and in the research log.
- Separate **signals** from **archive conclusions**.
- Keep **research importance** distinct from **build readiness**.
- Keep **freshness-sensitive facts** visible instead of paraphrasing them into timeless prose.

## Anti-sprawl rules
- Do not add more than one new top-band bundle in a revision unless another top-band file is being merged, retired, or substantially simplified.
- Prefer sharpening an existing Tier A candidate over minting another adjacent seam.
- If a new file is mostly a recombination of existing files, say so explicitly.
- Bundle docs should name their imported leaves and non-goals.
- Avoid creating multiple files that all claim to be the “real” current frontier.

## LLM-specific operating loop
Before making repo-shaping edits:
1. read `meta/ACTIVE_FRONTIER.md`;
2. read `meta/CANONICAL_WORKING_SET.md`;
3. read the newest block in `AGENTS.md` and `RESEARCH_LOG.md`;
4. read `meta/AMNESIA_RESISTORS.md`;
5. decide whether this revision is promotion, deepening, synthesis, or hygiene;
6. name the promoted candidate or explicitly say there is none.

While writing:
- keep question, evidence, alternatives, freshness, MVP, and non-goals distinct;
- do not silently rewrite rankings without naming the promotion / demotion;
- do not let one compelling source become the whole story when the archive is making a narrower claim.

After writing:
- mirror changed canonical files under `archive/`;
- regenerate `meta/ARCHIVE_MANIFEST.md`;
- verify the new revision summary in `INDEX.md` matches the actual changed file set.

## Default elimination rule
When several good candidates compete, prefer the one that:
- uses the most existing archive substrate,
- has the clearest machine-usable artifact family,
- solves a broadly recurring pain,
- and can help without becoming the one true platform.

If a revision cannot explain why the promoted candidate won on those axes, it should probably stay a research note instead of becoming the frontier.

- New (rev0403): harness/testing revisions must keep **subject discovery**, **capability declaration**, **harness semantics**, **runner/adapter behavior**, **run-result evidence**, and **specialized attachments/policy consumers** visibly separate; do not let one runner, one export format, or one CI wrapper silently become the whole testing story.
- New (rev0403): if a testing revision promotes the frontier, it must say whether it promoted the **pre-execution harness/adapter seam** or the broader **test-execution stack**; do not let one hot testing source silently flatten the upstream/downstream boundary.


## Maintenance-reality boundary rule
If a revision is about support posture, deprecation, succession, queue pressure, review routing, maintainer help, mentoring capacity, or fund/support-program inputs, it must say which layer it is changing:
- **lifecycle intent**,
- **workflow policy**,
- **observed stewardship state**,
- **derived pressure / continuity finding**,
- **help or succession routing**,
- **visibility / redaction posture**,
- or **consumer handoff**.

Default rule: never let one support-window declaration, one queue export, one help-request thread, one fund recommendation, or one assistant summary silently claim all seven layers at once.

## Performance-measurement promotion rule
If a revision promotes a benchmark/performance seam, it must say whether it changed **benchmark-native truth** or only **broader Perf Labs policy / gating**.

Default rule: never let “new measurement evidence contract” silently become “new universal performance policy”.
