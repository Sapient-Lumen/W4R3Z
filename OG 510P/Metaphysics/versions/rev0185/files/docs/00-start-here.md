# Start here — current rev0184 route

Current package: `Metaphysics-rev0185-2026.05.26.05.18-debt-cube-lifecycle-prioritization-audit-refactor.zip`  
Current final doc: `docs/189-source-cube-refactor-freshness-citation-audit-governance.md`

Use this route for the current session:

1. Read this file for release boundaries.
2. Read `README.md` for the front-door claim boundary.
3. Read `SOURCE_CROSSWALK_NORMALIZED.yml` and `SOURCE_CITATION_INDEX.yml` to see the expanded source inputs.
4. Read `CUBE/observations/sources.yml`, `CUBE/observations/source_relations.yml`, and `CUBE/observations/source_audit.yml` for the refactored source cube.
5. Treat all source rows as local, reviewable metadata. They do not prove source-currentness, source quality, conformance, or external review.

---

# Start here — current rev0181 route

This file now starts with the rev0181 reader route. Historical material below is retained as lineage.

Current package: `Metaphysics-rev0181-2026.05.25.21.34-current-release-normalization-cube-observation-expansion.zip`. Start with `CORE_THESIS_COMPRESSIONS.md` for a compact thesis, then choose a route from `READER_JOURNEY_MAP.yml`:

- Beginner: read the compression and the claim boundary before the full theory.
- Research: use `CONCEPT_CUBE.yml` and `DISCOVERY_BACKLOG.yml` to find operators, hard cases, rivals, and unresolved questions.
- Application: use `CLAIM_LANGUAGE_LEDGER.yml`, `DEBT_TAXONOMY.yml`, and `QUERY_REGRESSION_SUITE.yml` before reusing a distinction.
- Governance: use `CURRENT_RELEASE.yml`, `CONTROL_STACK.yml`, `CUBE/datasets.yml`, and `tools/validate_archive.py`.

New Bet 97: **currentness before confidence**. A release may not rely on a stale front-door identity, old allowed-claim language, or manifest-only cube rows when it is making current package claims.

New Bet 98: **observations before cube rhetoric**. A datacube claim should expose datasets, dimensions, measures, attributes, observations, sources, debts, and query surfaces before it is treated as analytic evidence.

## Historical start-here text follows

# Start Here

## Current release note — rev0181

Current release: `Metaphysics-rev0181-2026.05.25.21.34-current-release-normalization-cube-observation-expansion.zip`. Final numbered document: `docs/187-current-release-normalization-cube-observation-expansion-source-debt-access-concept-governance.md`. The front door is now governed by `CURRENT_RELEASE.yml`. Older revision text remains as historical lineage, not as active release identity.

Rev0181 adds a new reader rule: **availability is not comprehension, and a cube index is not yet an analytic cube unless claims, debts, sources, access barriers, and concepts are observable as rows.** Use `CUBE/datasets.yml` to choose an observation family before treating a claim as reusable.

## Four reader tracks

- Beginner: `CURRENT_RELEASE.yml` → `docs/00-start-here.md` → `README.md` current summary.
- Research: synthesis/operator files → `CONCEPT_CUBE.yml` → `DISCOVERY_BACKLOG.yml`.
- Application: `CUBE/observations/claims.yml` → `CUBE/observations/debts.yml` → `CLAIM_LANGUAGE_LEDGER.yml`.
- Governance: `CONTROL_STACK.yml` → `CUBE_INDEX.yml` → `QUERY_REGRESSION_SUITE.yml` → `tools/validate_archive.py`.

## Historical start-here material follows

# Start Here

## Archive objective

Develop a metaphysics that is:

- non-skeptical,
- non-reductive,
- ontologically serious,
- compatible with scientific inquiry without becoming subordinate to current theory,
- broad enough to unify the archive's main families: dependence and grounding; entityhood, unity, identity, and materiality; truth, facts, modality, properties, and abstracta; category discipline, status, objectivity, and metametaphysics; access, evidence, representation, and artifact-risk; social, normative, agential, personal, living, and conscious reality; process, time, persistence, transition, and irreversibility; stock, flow, availability, and material traffic; boundary, environment, support, and scaffolding; interface, placement, retention, surface, assembly, passage, and control relations,
- disciplined enough to resist decorative system-building and file-count expansion for its own sake,
- terminology-safe enough that ordinary words, aliases, source terms, metaphors, and family umbrellas do not silently decide ontology,
- commitment-safe enough that files, examples, useful distinctions, live rivals, source-local rules, and open debts do not silently become stronger doctrine than the archive has earned,
- application-auditable enough that reusable verdicts preserve their target, route, rivals, basis, grain, source role, hostile variants, non-verdict, status, maturity, future-use permission, open debts, and review triggers,
- precedent-safe enough that dossiered verdicts do not become unbounded slogans when reused, taught, transferred, appealed, superseded, or refused,
- transmission-safe enough that summaries, excerpts, diagrams, teaching examples, prompt answers, paper sections, rubrics, and derivative outputs preserve the limits appropriate to their compression level,
- reception-audited enough that uptake, misunderstanding, criticism, teaching failure, source-boundary failure, operational failure, errata, and package-drift signals are classified before feedback becomes doctrine,
- release-gated enough that edits, corrections, deprecations, hotfixes, rollbacks, open debts, migration paths, and package-verification results are classified before a versioned archive is treated as complete,
- lineage-governed enough that released packages, older versions, forks, derivatives, migrations, merges, teaching adaptations, and historical retentions are compared by explicit compatibility verdicts rather than assumed continuity,
- provenance-audited enough that packages, forks, derivatives, generated outputs, source-refresh branches, recovered copies, imports, and migrations carry evidence of origin, custody, transformation, validation, reproducibility, and trust status rather than gaining authority from polish or filenames alone,
- review-warrant-governed enough that self-checks, mechanical checks, source checks, provenance audits, adversarial reviews, external reviews, and public certification claims do not exceed their stated authority, scope, evidence, independence, and permitted claim language,
- public-reliance-governed enough that published, cited, taught, repeated, disputed, withdrawn, or retracted claims do not acquire broader permission than their version, status, review packet, source scope, and public-use packet allow,
- and stewardship-governed enough that public or derivative uses identify steward role, authority basis, accepted and declined duties, delegated authority, update/watch duty, warning duty, correction path, high-stakes boundary, and accountability consequence,
- continuity-register-governed enough that accepted duties, watch triggers, notice paths, closure evidence, derivative registries, source-watch items, public errata, fork declarations, and successor-memory records remain findable after the prose that created them has been read,
- validation-governed enough that schemas, transcripts, scripts, manifests, and machine-readable registers say what they check, what they do not check, what failed, what was waived, and what wording they permit,
- workflow-governed enough that release steps are executed through named runbooks, ordered stages, validation points, package points, fresh-extraction checks, and successor-readable handoff traces,
- automation-bounded enough that scripts, scheduled checks, generated drafts, validators, packaging tools, and delegated agents have explicit permissions, human-review gates, logs, forbidden claims, and stop conditions,
- and semantic-fidelity-governed enough that generated summaries, diagrams, tables, teaching handouts, prompt answers, source digests, and derivative excerpts preserve target, basis, status, warnings, non-verdicts, source boundaries, version limits, and public-use permissions before they are called faithful,
- deployment-boundary-governed enough that faithful outputs are not treated as policy, procedure, classifier, recommendation, automated trigger, operational guidance, or high-stakes advice until deployment status, action-reliance class, domain authority, affected parties, human override, notice path, rollback path, and forbidden use have been stated,
- and incident-response-governed enough that harmful uses, near misses, unauthorized escalations, warning failures, evidence losses, rollback failures, derivative misuses, and domain-sensitive reliance events are preserved, classified, contained, recovered, and closed only with residual risk and successor memory stated,
- and post-incident-learning-governed enough that recovered incidents, near misses, warning failures, and recovery disputes do not count as learned until root-cause profile, recurrence-risk class, corrective/preventive action, verification evidence, residual risk, and reopen trigger have been stated,
- and effectiveness-monitoring-governed enough that learned controls, warnings, validation checks, deployment boundaries, source-dependent limits, and sunset claims are reviewed for evidence of durability, residual-risk trend, renewal trigger, and retirement conditions rather than treated as permanently effective because they were verified once,
- and portfolio-governed enough that individually bounded risks, open debts, source dependencies, derivative permissions, deployment boundaries, incident patterns, monitoring duties, validation checks, and stewardship obligations are reviewed for exposure, correlation, cumulative burden, and priority treatment before the archive claims its risk posture is manageable,
- and capacity-allocation-governed enough that portfolio priorities, release debts, source-refresh needs, derivative duties, deployment-boundary reviews, incident lessons, monitoring triggers, validation gaps, and stewardship obligations do not count as handled until capacity status, backlog admission, work-in-progress class, deferral/resource-debt class, resource basis, owner or declined responsibility, next action, and forbidden claim language are explicit.
- and datacube-governed enough that current release records, control-stack steps, validation results, warning boundaries, capacity debts, source-crosswalk anchors, and forbidden public-use claims can be found as rows, checks, reports, or queryable artifacts rather than only as prose.



### Rev0165 schema-conformance and datacube-control artifacts

This revision adds `docs/171-schema-conformance-datacube-control-stack-and-queryable-governance.md`, `CONTROL_STACK.yml`, `CUBE_INDEX.yml`, `EXTERNAL_CROSSWALK.yml`, `REGISTERS/rev0166-schema-conformance.yml`, `REGISTERS/rev0166-control-stack.yml`, `REGISTERS/rev0166-datacube-index.yml`, `REGISTERS/schemas/schema-conformance-report-v1.yml`, `REGISTERS/schemas/control-stack-record-v1.yml`, `REGISTERS/schemas/datacube-index-record-v1.yml`, `RUNBOOKS/schema-conformance-datacube-review-v1.md`, and `tools/query_cube.py`. The local validator now checks current-record required-field conformance, control-stack continuity, cube observation shape, external-crosswalk structure, front-door artifact inclusion, and manifest integrity. These artifacts do not create public monitoring, source-watch service, standards compliance, public issue tracking, staffing, service levels, domain authority, or operational deployment.

## The archive's present answer

The current archive still favors a **synthesis** rather than a single inherited school:

> **Layered Process Realism**: reality is a stratified order of dynamically maintained forms and structures, in which entities are real as stabilized processual organizations, powers are ontologically serious, grounding orders dependence, teleology is real where organized domains earn it, and some higher-level domains are genuinely real without becoming metaphysically basic.

This revision is a **machine-readable datacube, canonical control-stack, schema-conformance, and query-governance revision** rather than a new first-order operator expansion. The previous pass asked whether portfolio priorities have actual capacity behind them. This pass asks whether the archive's own governance claims are represented as checkable fields, current-record schema conformance, canonical control-stack rows, cube observations, source artifacts, queryable debts, and forbidden claim language. Its new governing file is `docs/171-schema-conformance-datacube-control-stack-and-queryable-governance.md`.

Before the numbered sequence, this revision keeps the standing capacity constraint: **priority is not work done**. It adds a parallel machine-readability constraint: **schema is not conformance, register is not validation, repeated control prose is not a canonical control stack, and a cube metaphor is not a queryable cube**. Ordinary archive applications should still distinguish decision records, application dossiers, precedent packets, transmission packets, reception packets, release packets, lineage packets, provenance packets, review packets, public-reliance packets, stewardship packets, continuity registers, validation transcripts, workflow traces, automation records, semantic-fidelity records, deployment-boundary records, incident-response records, post-incident-learning records, effectiveness-monitoring records, and risk-portfolio records; but when a package, file, derivative, fork, teaching output, public handoff, citation, generated output, register, workflow, archive-derived classifier, deployment packet, preventive action, monitoring set, or portfolio item is described as assigned, scheduled, manageable, actively maintained, safe to defer, or handled, the archive should also record capacity status, backlog-admission class, work-in-progress class, deferral/resource-debt class, resource basis, owner or declined responsibility, next action, stop condition, allowed claim language, forbidden claim language, and open capacity debt.

Hundred-thirty-first, it now adopts an explicit **version-lineage / compatibility / fork / migration discipline**: the archive should not let old versions, current versions, forks, teaching derivatives, source-domain branches, hotfix lines, rollbacks, supersessions, citations, or migrations imply continuity until lineage relation, compatibility dimensions, compatibility class, changed items, retained items, migration action, allowed reuse, forbidden reuse, open lineage debt, and review trigger have been stated.

Hundred-thirty-second, it now adopts an explicit **provenance / custody / build-evidence / reproducibility discipline**: the archive should not let packages, forks, recovered copies, source-refresh branches, teaching derivatives, generated outputs, migrations, imports, or public handoffs acquire authority merely from a plausible filename, valid manifest, clean ZIP, or familiar prose; it should record source artifact, custody path, edit intent, transformation actions, touched files, generated material, tools/procedures, verification evidence, reproducibility status, tamper signals checked, allowed trust, known omissions, and review trigger before treating an artifact as clean, rebuildable, importable, or safe to cite.


Hundred-thirty-third, it now adopts an explicit **review-authority / audit-certification / claim-warrant discipline**: the archive should not let packages, files, source-dependent examples, migration packets, release packets, provenance packets, teaching derivatives, public claims, or external references use words like reviewed, audited, certified, validated, approved, source-reviewed, externally reviewed, or release-warranted until the reviewer role, authority basis, independence status, review scope, out-of-scope limits, evidence inspected, controls run, findings, certification status, allowed wording, forbidden wording, conflicts, expiry triggers, and return path have been stated.

Hundred-thirty-fourth, it now adopts an explicit **public-reliance / citation / dispute / withdrawal / retraction discipline**: the archive should not let a reviewed, released, transmitted, taught, or cited claim function as a public reliance object until the public-use status, intended audience, permitted use, forbidden use, required warnings, citation form, dispute path, update/notice path, expiry trigger, and withdrawal or retraction rule have been stated.

Hundred-thirty-fifth, it now adopts an explicit **stewardship / obligations / delegated-authority / accountability discipline**: the archive should not let a public-use permission, teaching reuse, fork, derivative, generated output, source-domain adaptation, or citation become responsibly maintained until steward role, authority basis, authority limits, obligation class, accepted duties, declined duties, delegation or handoff, update/watch trigger, warning duty, correction path, high-stakes boundary, accountability consequence, and expiry or review trigger have been stated.


Hundred-thirty-sixth, it now adopts an explicit **operational-register / watch-queue / continuity-memory discipline**: the archive should not let accepted duties, source-watch needs, review expiries, public-reliance limits, correction notices, derivative registries, fork declarations, withdrawal rules, migration notes, closure evidence, or successor-memory fields remain only in prose when they must be findable, awakened, closed, inherited, or marked as open debt.

Hundred-thirty-seventh, it now adopts an explicit **validation-harness / invariant-check / machine-readable-governance discipline**: the archive should not let schemas, YAML records, validation transcripts, scripts, dashboards, manifests, or tidy register files imply more than they checked; each validation claim should state schema, invariant family, check mode, pass/fail/not-run results, failure severity, human-review boundary, allowed wording, forbidden wording, and next trigger.

Hundred-thirty-eighth, it now adopts an explicit **release-workflow / runbook / execution-trace discipline**: the archive should not treat a package as workflow-controlled merely because the final files look clean; it should record runbook identity, stage order, entry and exit criteria, validation point, manifest/package point, fresh-extraction result, skipped stages, exceptions, handoff limits, and open workflow debt.

Hundred-thirty-ninth, it now adopts an explicit **automation-boundary / delegated-agent / scheduled-execution discipline**: the archive should not let scripts, validators, generated drafts, packaging tools, scheduled checks, search systems, or delegated agents acquire philosophical authority, source authority, public maintenance status, domain authority, or stewardship authority merely because they executed; tool permission, human-review gate, evidence record, stop condition, and forbidden claims must be explicit.

Hundred-fortieth, it now adopts an explicit **semantic-fidelity / generated-output / warning-retention discipline**: the archive should not call a summary, diagram, table, teaching handout, generated answer, source digest, derivative excerpt, public handoff, or release note faithful merely because it is fluent, authorized, validated, or well formatted; it should preserve target, route, basis, status, non-verdict, source boundary, version limit, warning, allowed reuse, forbidden reuse, and correction trigger.

Hundred-forty-first, it now adopts an explicit **operational-reliance / deployment-boundary / action-use discipline**: the archive should not let even a faithful output become policy, procedure, classifier, recommendation, automated trigger, workflow rule, institutional decision support, or high-stakes advice until deployment status, action-reliance class, affected parties, domain/source-current review, human override, notice path, appeal path, rollback path, monitoring requirement, permitted actions, and forbidden actions have been stated.

Hundred-forty-second, it now adopts an explicit **incident-response / harm-review / near-miss / recovery discipline**: the archive should not treat harmful use, near miss, unauthorized operational escalation, warning failure, evidence loss, derivative misuse, public reliance failure, rollback failure, or domain-sensitive reliance event as ordinary feedback; it should preserve evidence, classify incident status, harm severity, recovery class, affected scope, containment action, notice path, rollback/withdrawal/correction path, root-cause hypothesis, residual risk, closure evidence, and successor-memory trigger before the event is closed or forgotten.

Hundred-forty-third, it now adopts an explicit **post-incident learning / root-cause / corrective-preventive action / recurrence-risk discipline**: the archive should not treat a recovered incident, near miss, warning failure, deployment-boundary failure, derivative misuse, public-reliance failure, validation misclaim, or recovery dispute as learned until learning status, root-cause profile, recurrence-risk class, corrective action, preventive action, verification evidence, affected artifacts, residual risk, and reopen trigger have been stated.

Hundred-forty-fourth, it now adopts an explicit **longitudinal monitoring / effectiveness-review / residual-risk / sunset-renewal discipline**: the archive should not treat a learned control, warning, validation check, deployment boundary, source-dependent limit, derivative restriction, release gate, or post-incident preventive action as durable merely because it was verified once; monitoring status, evidence basis, effectiveness class, residual-risk trend, review trigger, escalation route, and sunset or renewal condition must be stated before the archive says the control remains effective, should be retired, or no longer needs attention.

Hundred-forty-fifth, it now adopts an explicit **cross-case risk-portfolio / systemic-exposure / prioritization discipline**: the archive should not treat individually bounded residual risks as collectively manageable until portfolio status, exposure aggregation, shared dependency, common-cause failure, cumulative review burden, source-refresh burden, public-use exposure, deployment exposure, priority treatment, owner or declined responsibility, and next review trigger have been stated.

Hundred-forty-sixth, it now adopts an explicit **capacity-planning / backlog-admission / work-in-progress / deferral discipline**: the archive should not treat prioritized work as handled until capacity status, backlog-admission class, work-in-progress class, deferral/resource-debt class, resource basis, scarce dependency, owner or declined responsibility, next action, stop condition, allowed claim language, forbidden claim language, and open capacity debt have been stated.

## Main archive bets

### Bet 1: Reality is not flat

Some things are more basic than others, but reality is not exhausted by whatever is most basic.

### Bet 2: Being includes becoming

A satisfactory metaphysics must explain persistence, development, and decay without treating change as a mere illusion or bookkeeping artifact.

### Bet 3: Identity is partly organizational

What a thing is cannot always be recovered from its material constituents considered apart from form, history, and ongoing organization.

### Bet 4: Dependence is real but not uniform

Grounding, constitution, realization, composition, and ontological dependence matter. Yet it does not follow that every case should be redescribed as one master relation.

### Bet 5A: Inquiry is corrigible without being ontologically empty

Theory change should often revise ontology in typed ways—preservation, reinterpretation, split, merge, demotion, elimination—rather than forcing either flat continuity or skepticism.

### Bet 6: Powers belong in ontology

A world of wholly inert categorical items leaves tendency, lawfulness, capacity, and production underdescribed.

### Bet 6A: Entityhood is not brute counting

What counts as one thing, and what makes it persist, depends in part on kind, form, and organized continuity.

### Bet 7: Absence is often derivative but sometimes ontologically serious

Lack, defect, omission, and privation should not be treated either as always unreal or as automatically requiring a bespoke negative entity.

### Bet 8: Some repeatables and kinds are real enough to matter

A good metaphysics needs resources for real similarity, powers, lawfulness, and kind-sensitive persistence without reifying every successful predicate.

### Bet 9: Modal space is structured by what things are

Metaphysical possibility is not whatever we can coherently imagine. It is constrained by essence, powers, structure, and constitutive profile.

### Bet 10: Category mistakes are a major source of metaphysical confusion

Objects, processes, relations, facts, and kinds are not interchangeable. Many pseudo-disputes arise because one category is silently treated as if it had the logic of another.

### Bet 11: Wholes are not exhausted by parts

A plurality of parts does not automatically amount to one serious individual. Integration, boundary type, and part-turnover tolerance matter alongside composition.

### Bet 12: Causation is worldly difference-making, not only a modeling convenience

Counterfactuals and interventions are indispensable for diagnosing causal structure, but the archive should still treat production, prevention, sustaining, and blocked support as metaphysically serious features of a power-bearing processual world.

### Bet 13: Time is real, but its metaphysics should not be settled too cheaply

A satisfactory metaphysics should treat temporal order, change, persistence, and irreversibility as real while resisting the temptation to identify all of time metaphysics with one quick verdict about presentism, eternalism, or the growing block.

### Bet 14: Place matters, but occupancy alone does not settle ontology

A satisfactory metaphysics should treat location, adjacency, region, and situated interaction as real while resisting the temptation to infer identity, constitution, or a final theory of space merely from co-location or ordinary place-talk.

### Bet 15: Existence claims need their own discipline

A satisfactory metaphysics should distinguish what exists from what is fundamental, what is robustly real from what is thinly dependent, and what is ontologically serious from what is merely representationally convenient.

### Bet 15A: Ontological status should be explicit rather than ambient

A satisfactory metaphysics should distinguish derivative but robust reality from thin dependence, idealized but world-tracking posits from mere fiction, and status verdicts from bare existential grammar.

### Bet 16: Some individuals earn substance-like bearerhood without requiring bare substrata

A satisfactory metaphysics should allow persisting, organized subjects of change where the domain earns them, while preferring formed, power-bearing, process-sustained individuals over featureless underlying cores.

### Bet 17: Teleology is real where organization earns it

A satisfactory metaphysics should distinguish selected functions, self-maintaining organizational roles, designed purposes, agential goals, and institutional ends rather than either eliminating purposive structure or inflating it into a global design thesis.

### Bet 18: Some abstracta are real enough to matter, but not all in the same way

A satisfactory metaphysics should distinguish mathematical objects, propositions, structures, and idealized entities rather than either inflating them into one detached realm or eliminating them with a costless paraphrase gesture.

### Bet 19: Becoming often requires a typed act/potency profile

A satisfactory metaphysics should distinguish bare possibility from real power, standing capacity from organized readiness, ongoing actualization from achieved fulfillment, and frustration from mere non-occurrence.

### Bet 20: Relations are real, but only under typed discipline

A satisfactory metaphysics should distinguish internal from external relations, thin order from thick constitutive or productive linkage, and local structural holism from vague global connectedness.

### Bet 21: Levels are real, but level-talk must be typed

A satisfactory metaphysics should distinguish metaphysical fundamentality from explanatory level, local mechanistic stratification, scale, descriptive resolution, and cross-level constraint rather than treating all “higher” and “lower” vocabulary as one ladder.

### Bet 22: Some classifications carve better than others, but not always by one global recipe

A satisfactory metaphysics should distinguish mere predicability or usefulness from comparative naturalness, and should allow disciplined local joint-carving without assuming that only one final vocabulary can serve every real domain.

### Bet 23: The right grain often matters as much as the right ontology

A satisfactory metaphysics should distinguish determinables from determinates, explanatory proportion from mere descriptive precision, and finer grain from deeper reality rather than treating every increase in specificity as metaphysical progress.

### Bet 24: No-free-floating-difference claims need stronger follow-up

A satisfactory metaphysics should use supervenience to block unmotivated autonomy, but should not mistake modal covariance for the fuller metaphysics of realization, grounding, reduction, or explanatory completeness.

### Bet 25: Architectural direction is real, but not every loop is vicious

A satisfactory metaphysics should preserve some typed ontological direction while distinguishing metaphysical dependence loops from causal, functional, and regulatory feedback, and while allowing that some infinite or reciprocal structures may still be anchored rather than directionless.

### Bet 26: Not every target of thought or discourse needs the same ontology

A satisfactory metaphysics should distinguish fictional entities, mythical beings, failed theoretical posits, merely possible individuals, intentional targets, and impossible descriptions rather than forcing them all into one flat verdict of either full existence or total eliminability.

### Bet 27: Coincidence does not settle constitution or identity by itself

A satisfactory metaphysics should distinguish co-location, material continuity, constitution, identity, and realization rather than inferring too quickly that shared place means one thing, or that divergent profiles automatically mean two.

### Bet 28: Concrete being comes in more than one serious mode

A satisfactory metaphysics should allow concrete reality to be thing-like, stuff-like, field-like, medium-like, or distributed without treating compact countability as the sole measure of ontological seriousness.

### Bet 29: Aboutness is real, but content needs typed discipline

A satisfactory metaphysics should distinguish signal from meaning, vehicle from content, model from target, and documentary representation from proposition-like truth-bearing content rather than treating all representation as one flat semantic or ontological phenomenon.

### Bet 30: Some transformation-related differences are merely presentational

A satisfactory metaphysics should distinguish invariant structure from gauge-like redundancy, transformed presentation, and broken symmetry rather than treating every formal difference as a difference in the furniture of reality.

### Bet 31: Objective uncertainty is real where processes and laws earn it

A satisfactory metaphysics should distinguish credence, evidence, frequency, model-parameter probability, and genuine chance rather than treating every probabilistic description as either mere ignorance or immediate proof of fundamental indeterminism.

### Bet 32: Granularity is real, but resolution-talk must be typed

A satisfactory metaphysics should distinguish continuity from discreteness, ontological grain from measurement grain, and quantization from mere sampling or thresholding rather than treating every difference in resolution as a verdict on what reality is made of.

### Bet 33: Some truths are centered without being merely subjective

A satisfactory metaphysics should distinguish world-description from self-location, objective centered facts from merely private perspective, and role- or interface-position from mere semantic decoration rather than treating every “I/here/now/actual/current” fact as flattenable without loss.

### Bet 34: Consciousness is real, but it needs typed dependence discipline

A satisfactory metaphysics should distinguish phenomenality from access, report, attention, and self-interpretation, and should distinguish correlation from realization, grounding, identity, and emergence rather than treating every conscious case as either already reduced or already metaphysically detached.

### Bet 35: Form is real, but it is not a second stuff

A satisfactory metaphysics should distinguish material basis, organizational form, visible shape, functional role, and kind-sensitive unity rather than treating every appeal to form as either spooky dualism or merely decorative description.

### Bet 36: Processes are real, but not every happening has the same logic

A satisfactory metaphysics should distinguish events, activities, accomplishments, achievements, states, maintenance processes, and process-sustained individuals rather than treating every dynamic case as either one more static object-change or one undifferentiated flow.

### Bet 37: The world is a serious totality, but world-talk must be typed

A satisfactory metaphysics should distinguish the actual cosmos from possible-worlds apparatus, existence monism from priority monism, global structure from one concrete super-object, and domain-totalities from the world as such rather than letting one use of “the world” settle the ontology.

### Bet 38: Appearance is world-involving, but appearance-talk must be typed

A satisfactory metaphysics should distinguish veridical presentation from illusion, phenomenal manifestation from mere reportability, manifest-image reality from final ontology, and scientific revision from eliminative triumphalism rather than letting one use of “appearance” or “manifest” settle the metaphysics.

### Bet 39: Powers are real, but power-talk must be typed

A satisfactory metaphysics should distinguish dispositions from abilities, standing powers from current opportunities, manifestation from possession, and masking or mimicking conditions from the powers themselves rather than letting one use of “can”, “capacity”, or “disposition” settle laws, causation, agency, and modality all at once.

### Bet 40: Objectivity is real, but objectivity-talk must be typed

A satisfactory metaphysics should distinguish mind-independence from observer-sensitivity, response-dependence from mere projection, institutionally objective order from private preference, and centered facts from merely subjective reports rather than letting one use of “objective” or “subjective” settle the ontology.


### Bet 41: Evidence is world-constrained, but evidence-talk must be typed

A satisfactory metaphysics should distinguish data from evidence, confirmation from truth, first-order support from second-order historical pressure, and underdetermination from wholesale skepticism rather than letting one appeal to “what the evidence shows” settle ontology all at once.

### Bet 42: Error is real, but failure-mode talk must be typed

A satisfactory metaphysics should distinguish illusion from hallucination, distortion from fabrication, proxy failure from target absence, setup artifact from ontological defeat, and theory-ladenness from arbitrariness rather than letting one use of “artifact”, “bias”, “noise”, or “only a model effect” settle the metaphysics all at once.

### Bet 43: Reference is real, but reference-talk must be typed

A satisfactory metaphysics should distinguish naming from denotation, denotation from representation, lexical continuity from target continuity, centered anchoring from mere subjectivity, and proxy capture from target-fixation rather than letting one use of “refers to”, “tracks”, “this”, or “the same target” settle the ontology all at once.

### Bet 44: Comparative choice is real, but rivalry-talk must be typed

A satisfactory metaphysics should distinguish genuine ontological incompatibility from grain-shift, category-shift, layered coexistence, and pragmatic redescription rather than letting one use of “rival package”, “better ontology”, “same target under another description”, or “plural but compatible” settle the metaphysics all at once.

### Bet 45: Reformulation is real, but equivalence-talk must be typed

A satisfactory metaphysics should distinguish empirical equivalence, formal equivalence, interpretive equivalence, gauge-style redundancy, duality, and genuine ontological sameness rather than letting one use of “same theory”, “mere reformulation”, “dual description”, or “equivalent package” settle the metaphysics all at once.

### Bet 46: Scaffolding is real, but support-talk must be typed

A satisfactory metaphysics should distinguish enabling condition from constitutive part, persistent scaffold from transient aid, developmental niche from mere background environment, and external support from bearer-erasing diffusion rather than letting one use of “distributed”, “offloaded”, “scaffolded”, or “extended” settle ontology all at once.

### Bet 47: Resilience is real, but survival-through-disturbance must be typed

A satisfactory metaphysics should distinguish persistence from resilience, repair from replacement, plastic reorganization from identity indifference, and adaptive change from mere temporary compensation rather than letting one use of “recovery”, “bouncing back”, “same thing after damage”, or “it still functions” settle ontology all at once.

### Bet 48: Dormancy is real, but quiet-phase persistence must be typed

A satisfactory metaphysics should distinguish inactivity from nonbeing, dormancy from death, latency from bare possibility, and suspended exercise from loss rather than letting one use of “inactive”, “asleep”, “on standby”, “dormant”, or “not currently manifesting” settle ontology all at once.

### Bet 49: Delegated enactment is real, but action-through-others must be typed

A satisfactory metaphysics should distinguish delegated execution from replacement, proxying from identity, office enactment from private action, shared action from corporate agency, and controlled handoff from simple succession rather than letting one use of “through”, “on behalf of”, “the system decided”, “the institution acted”, or “someone else carried it out” settle ontology all at once.


### Bet 50: Blocked manifestation is real, but non-display must be typed

A satisfactory metaphysics should distinguish untriggered capacity from masked manifestation, internal inhibition from external prevention, strategic withholding from dormancy, and suppressed expression from genuine loss rather than letting one use of "blocked", "silent", "not expressed", or "not showing up" settle ontology all at once.

### Bet 51: Onset is real, but coming-online must be typed

A satisfactory metaphysics should distinguish onset from creation, activation from mere permission, threshold crossing from arbitrary cutoff, release from fresh acquisition, and phase-entry from new bearerhood rather than letting one use of "turned on", "began", "came online", "crossed threshold", or "suddenly appeared" settle ontology all at once.

### Bet 52: Cessation is real, but going-offline must be typed

A satisfactory metaphysics should distinguish deactivation from death, revocation from destruction, dissolution from mere dispersal, end of manifestation from end of basis, and terminal ending from temporary offlining rather than letting one use of "stopped", "ended", "expired", "went offline", "was revoked", or "died" settle ontology all at once.

### Bet 53: Return is real, but coming-back must be typed

A satisfactory metaphysics should distinguish resumption from repetition, reactivation from reinstatement, restart from repair, cyclical return from uninterrupted persistence, and record-backed restoration from live bearer continuity rather than letting one use of "came back", "resumed", "returned", or "was restored" settle identity and persistence all at once.

### Bet 54: Succession is real, but continuity-through-replacement must be typed

A satisfactory metaphysics should distinguish persistence from succession, lineage continuity from mere kind-membership, office continuity from office-holder identity, charter continuity from nominal inheritance, and design or tradition inheritance from token identity rather than letting one use of "same institution", "same line", "same office", or "handed down" settle identity and persistence all at once.

### Bet 55: Multiplication is real, but one-becomes-many cases must be typed

A satisfactory metaphysics should distinguish persistence from duplication, copying from reproduction, branching continuity from linear succession, archive-based re-instantiation from simple return, and type continuity from token continuity rather than letting one use of "same again", "copied", "cloned", "split", or "forked" settle identity and persistence all at once.

### Bet 56: Convergent unity is real, but many-become-one cases must be typed

A satisfactory metaphysics should distinguish coordination from fusion, aggregation from organized unity, composition from constitution, absorption from symmetric merger, higher-order bearerhood from simple administrative bundling, and predecessor continuity from predecessor erasure rather than letting one use of "merged", "fused", "became one", or "integrated" settle unity and counting all at once.

### Bet 57: Overlap is real, but shared-commonality cases must be typed

A satisfactory metaphysics should distinguish shared proper parts from shared location, complete coincidence from partial overlap, interpenetration from ordinary overlap, member/resource overlap from merger, and stable overlap from transitional overlap rather than letting one use of "overlaps", "shares parts", "partly coincides", or "is not wholly disjoint" settle identity, constitution, or fusion all at once.

### Bet 58: Counteraction is real, but no-net-effect cases must be typed

A satisfactory metaphysics should distinguish contradiction from opposition, absence from net cancellation, compensation from exact neutralization, inhibition from double prevention, active equilibrium from passive rest, and measured flatness from underlying antagonistic activity rather than letting one use of "cancels", "offsets", "balances", "neutralizes", or "no net effect" settle ontology and causation all at once.

### Bet 59: Redundancy is real, but many-enough cases must be typed

A satisfactory metaphysics should distinguish joint necessity from co-sufficiency, genuine simultaneous overdetermination from preempted backup, redundancy from degeneracy, standing reserve from active contribution, and failover continuity from strict pathway identity rather than letting one use of "redundant", "backed up", "either would have done", "failover", or "more than one sufficient route" settle causation, persistence, and explanatory privilege all at once.

### Bet 60: Amplification is real, but stronger-together cases must be typed

A satisfactory metaphysics should distinguish simple addition from cooperative synergy, catalytic enablement from material contribution, positive-feedback amplification from runaway escalation, recruitment cascades from standby backup, and autocatalytic expansion from mere repetition rather than letting one use of "synergy", "catalytic", "snowballing", "feeds on itself", or "more than additive" settle causation, organization, or level privilege all at once.

### Bet 61: Stabilization is real, but self-limiting cases must be typed

A satisfactory metaphysics should distinguish passive damping from active regulation, buffering reserve from feedback correction, homeostatic range-maintenance from rigid fixed-point stillness, adaptive retuning from mere return, and dynamic equilibrium from inactivity rather than letting one use of "stable", "regulated", "buffered", "homeostatic", or "returns to baseline" settle causation, organization, or control all at once.



### Bet 62: Selective responsiveness is real, but gating and coupling cases must be typed

A satisfactory metaphysics should distinguish standing receptivity from current uptake, windowed gating from indiscriminate openness, tuned sensitivity from identity or fusion, coupling-strength modulation from all-or-nothing linkage, switch-like route selection from creation or annihilation, and communication-window fit from full synchronization rather than letting one use of "gated", "tuned", "coupled", "responsive", "windowed", or "switch-like" settle openness, control, and organization all at once.

### Bet 63: Capacity limits are real, but ceiling and refractory cases must be typed

A satisfactory metaphysics should distinguish saturation from absence, refractory silence from disappearance, bottleneck constraint from total disconnection, reserve drawdown from annihilation, overload from ordinary stronger activation, and protective throttling from simple failure rather than letting one use of "saturated", "at capacity", "overloaded", "refractory", "bottlenecked", or "maxed out" settle ontology, organization, and control all at once.

### Bet 64: History-shaped responsiveness is real, but repetition-driven recalibration must be typed

A satisfactory metaphysics should distinguish habituation from fatigue, sensitization from simple stronger activation, desensitization from disappearance, local recalibration from whole-system shift, allostatic retuning from mere return to baseline, and long-run response change from outright replacement rather than letting one use of "used to it", "sensitized", "desensitized", "tolerant", "numbed", or "recalibrated" settle ontology and persistence all at once.


### Bet 65: Real transitions are typed, but tipping cases must distinguish movement within a landscape from reorganization of the landscape itself

A satisfactory metaphysics should distinguish threshold entry within a fixed landscape from resilience loss, resilience loss from actual tipping, bifurcation from mere activation, hysteretic return asymmetry from ordinary delay, basin loss from temporary suppression, and apparent tipping from genuine landscape reorganization rather than letting one use of "critical threshold", "tipping point", "collapse", "bifurcated", or "passed the point of no return" settle ontology, persistence, and explanation all at once.

### Bet 66: Interface relations are real, but interface-talk must be typed

Substitution, hosting, attachment, insertion, enclosure, layering, joining, retention, and guided passage are not interchangeable ways of saying that one thing is “with” another. They mark different ways in which targets, supports, sites, layers, openings, interfaces, and control structures can matter without automatically settling identity, parthood, or fusion.

### Bet 67: Passage and control are real, but flow-language must be typed

Throughflow, bottlenecking, rerouting, guidance, sealing, leakage, gating, and valving are adjacent but not identical. A serious case must say whether the explanatory burden falls on route, constraint, alternate path, boundary closure, uncontrolled escape, selective permission, or regulated quantity/rate.

### Bet 68: Continuity claims must identify the preserving relation

A target can persist through replacement, migration, hosting, support change, fastener change, guide change, or valve-setting change, but not because “same function,” “same line,” “same host,” “same interface,” or “same control hardware” says so by itself. The preserving relation has to be stated at the right grain.

### Bet 69: Operator choice is triage before expansion

The archive is now large enough that future additions should first be routed through a family map. A new operator earns its place only if existing families, nearest-neighbor files, basis tests, grain tests, failure modes, continuity consequences, and artifact-risk checks leave a genuine compression gap.

### Bet 70: A mature archive must try to break its own classifications

The archive is now large enough that false confidence can come from too many good distinctions as well as too few. A satisfactory metaphysical method should therefore red-team its own preferred verdicts: preserve the word while changing the basis, preserve the basis while changing the word, shift the grain, vary the proxy evidence, test duplication or fission, and state defeaters before treating a routed case as settled.

### Bet 71: Hard cases should become calibration instruments, not anecdotes

A satisfactory metaphysical method should preserve the tested path of its difficult verdicts. Once a case becomes reusable or precedential, the archive should record positive controls, negative controls, hard positives, hard negatives, boundary cases, regression instructions, artifact risks, defeaters, continuity consequences, and open debt. Otherwise examples become trophies rather than tests.

### Bet 72: Accepted changes must propagate through the archive

A satisfactory metaphysical research archive should not let local insight become global drift. When a revision changes doctrine, method, routing, calibration, source dependence, or package structure, its downstream commitments should be updated, explicitly declined, or ledgered as open debt across the files that a future reader or future revision will rely on.

### Bet 73: Vocabulary must be registered before it becomes doctrine

A satisfactory metaphysical research archive should not let ordinary words, aliases, metaphors, or source-specific terms settle identity, dependence, parthood, continuity, status, evidence, or causation by momentum. Durable terms should be assigned a status — canonical operator term, alias, family umbrella, neighboring rival, domain-specific term, diagnostic prompt, source-specific anchor, deprecated term, quarantined metaphor, or unsafe shortcut — before they carry stable operator-work.

### Bet 74: Commitment levels must be assigned before they become doctrine

A satisfactory metaphysical research archive should not let a file title, useful distinction, vivid example, ledgered case, source-local rule, or synthesis phrase sound stronger than it is. Durable claims should be assigned a commitment status and maturity level — kernel commitment, working default, mature diagnostic distinction, calibrated precedent, domain-local rule, live rival, provisional probe, quarantined analogy, source-dependent commitment, deprecated / compressed / absorbed item, or open debt; M0 through M8 — before they are used to guide further expansion or front-door doctrine.

### Bet 75: Application verdicts need portable dossiers before they travel

A satisfactory metaphysical research archive should not let reusable verdicts remain scattered across private reasoning, method notes, and confident summaries. When a result will guide teaching, precedent, calibration, source interpretation, or revision, it should record target, route, rivals, basis, grain, source role, hostile variants, artifact risks, terminology status, commitment status, verdict, non-verdict, future-use permission, open debts, and review trigger.

### Bet 76: Precedents need reuse, transfer, appeal, and supersession rules

A satisfactory metaphysical research archive should not let a dossiered verdict become an unbounded slogan. Later uses should state whether the result is local answer, teaching illustration, controlled precedent, calibration precedent, regression warning, source-bound precedent, live-rival precedent, deprecated caution, appeal-pending item, or do-not-reuse item; and they should reopen the verdict when target, basis, grain, family, source role, term status, commitment status, non-verdict, or failure mode no longer transfers.

### Bet 77: Transmission needs compression and pedagogical discipline

A satisfactory metaphysical research archive should not let summaries, excerpts, diagrams, tables, prompt answers, teaching modules, paper sections, rubrics, or derivative artifacts become stronger than the verdicts they compress. A traveling output should state its compression level, audience/use, omitted material, minimum retained limits, warning, and return path rather than making orientation sound like doctrine or teaching illustration sound like calibration.

### Bet 78: Reception feedback needs correction-loop governance before it becomes doctrine

A satisfactory metaphysical research archive should not let uptake, misunderstanding, criticism, teaching failure, source-boundary failure, operational failure, errata notice, repeated citation, or reuse request revise doctrine by pressure alone. Feedback should be classified as accurate uptake, orientation gap, wording ambiguity, warning failure, return-path failure, status bleaching, precedent misuse, source-boundary failure, genuine counterexample pressure, or package-drift signal before the archive decides whether to reply locally, repair wording, add warning, update a packet, open appeal, ledger a case, propagate a correction, quarantine an output, or reopen doctrine.

### Bet 79: Releases need gates, ledgers, migration paths, and rollback triggers

A correction is not yet a release, a manifest is not conceptual readiness, and deprecation is not erasure. The archive should state release class, affected files, gate outcomes, open debts, deprecations, migration notes, source implications, verification evidence, and rollback triggers before treating a package as complete.

### Bet 80: Version succession is not compatibility

A later package is not automatically a compatible continuation, and an older package is not automatically obsolete for every purpose. A satisfactory research archive should state lineage relation, compatibility class, migration rule, allowed reuse, forbidden reuse, and open lineage debt before citing old material as current, importing a fork, merging a branch, migrating teaching artifacts, or treating historical retention as live doctrine.

### Bet 81: Artifact authority requires provenance, custody, and reproducibility evidence

A clean-looking package is not automatically a trustworthy package, and a valid manifest is not automatically a build history. A satisfactory research archive should state source artifact, custody path, edit intent, transformations, touched files, generated material, tools/procedures, verification evidence, reproducibility status, tamper signals checked, allowed trust, and open provenance debt before treating a package, fork, derivative, recovered copy, imported branch, or source-refresh artifact as clean, rebuildable, importable, or safe to cite.


### Bet 82: Review is scoped warrant, not general authority

A self-check is not an external review, a manifest check is not a philosophical endorsement, a source review is not archive-wide doctrine, and a provenance audit is not conceptual certification. A satisfactory research archive should state reviewer role, authority basis, independence status, scope, evidence, findings, certification status, permitted claim language, conflicts, expiry triggers, and return path before saying that a package, claim, file, derivative, or release is reviewed, audited, certified, validated, approved, or release-warranted.

### Bet 83: Public reliance is a separate permission

A satisfactory research archive should not let publication, repeated citation, teaching uptake, review language, or package polish become unrestricted public authority. Public use should state version identity, public-use status, intended audience, permitted and forbidden uses, required warnings, citation form, dispute path, update path, expiry trigger, and withdrawal or retraction rule before a claim is allowed to travel as something others may rely on.

### Bet 84: Reliance permission creates stewardship duties

A satisfactory research archive should not let permitted public use become abandoned responsibility or unlimited liability. Maintainers, reviewers, citers, teachers, fork maintainers, derivative authors, source-domain adapters, automated-output stewards, and public relying users should state what authority they have, what duties they accept, what duties they decline, what warnings and updates they must preserve, how disputes and corrections route, when high-stakes use requires domain review, and what consequence follows if those duties fail.

### Bet 85: Duties need operational memory

A satisfactory research archive should not let accepted obligations survive only as prose, private memory, or good intention. Maintained public and derivative uses should state register type, controlling packet, responsible role, continuity status, watch trigger, notice path, closure evidence, open debt, and successor-memory field before claiming that an update-watch, correction, source-refresh, derivative registry, fork declaration, public errata, withdrawal, migration, or handoff duty is operational.

### Bet 86: Machine-readable discipline must not become machine-readable authority

A satisfactory research archive should not let schemas, YAML files, validation transcripts, scripts, manifests, checklists, dashboards, or register fields launder stronger claims than they actually check. Validation should state its schema, required fields, invariant families, check mode, passed checks, failed checks, skipped checks, exceptions, human-review boundary, closure evidence, allowed wording, forbidden wording, and next trigger before a package, packet, register, derivative, fork, or release is described as validation-backed.

### Bet 87: Workflow traces are release memory, not authority inflation

A satisfactory research archive should not let a clean ZIP, valid manifest, passing script, or polished release note substitute for a controlled release process. Workflow claims should state runbook, stage order, entry and exit criteria, evidence artifacts, validation point, package point, fresh-extraction result, skipped stages, handoff limits, allowed wording, forbidden wording, open workflow debt, and next trigger before a package is described as workflow-controlled, runbook-executed, handoff-ready, or repeatably produced.

### Bet 88: Automation must remain bounded by permission, evidence, and review

A satisfactory research archive should not let scripts, validators, generated drafts, scheduled reminders, packaging tools, or delegated agents acquire authority merely because they executed successfully. Automation claims should state automation status, tool-permission class, scheduled-execution class, authorized scope, prohibited scope, human-review gate, evidence artifact, allowed wording, forbidden wording, stop condition, open automation debt, and next review trigger before a result is described as automated, monitored, source-current, independently reproduced, publicly maintained, or tool-certified.

### Bet 89: Semantic fidelity is warning-retaining transfer, not polish

A satisfactory research archive should not let a fluent summary, clean table, elegant diagram, useful teaching handout, generated answer, source digest, or derivative excerpt count as faithful merely because it is clear or tool-authorized. Faithful transfer should preserve source version, target, route, basis, status, non-verdict, warnings, source boundaries, public-use limits, and forbidden upgrades before an output is described as archive-faithful, teaching-safe, source-preserving, or derivative-ready.

### Bet 90: Faithful output is not operational authorization

A satisfactory research archive should not let accurate summaries, clean diagrams, validated registers, teaching handouts, generated answers, or public notes become policy, procedure, classifier, recommendation, automated trigger, or high-stakes guidance merely because they are faithful to the archive. Operational use should state deployment status, action-reliance class, affected parties, domain/source-current review, human override, notice path, rollback path, monitoring requirement, permitted actions, forbidden actions, and open deployment debt.

### Bet 91: Incidents require recovery memory, not embarrassment management

A satisfactory research archive should not treat harmful use, near miss, unauthorized escalation, warning failure, evidence loss, derivative misuse, public reliance failure, rollback failure, or domain-sensitive reliance event as ordinary feedback or private embarrassment. Incident handling should preserve evidence, classify incident status, harm severity, recovery class, affected scope, containment action, notice path, rollback/withdrawal/correction path, root-cause hypothesis, residual risk, closure evidence, and successor-memory trigger before the event is closed.

### Bet 92: Recovery is not learning until recurrence has a control

A satisfactory research archive should not treat a recovered incident or near miss as learned merely because the visible problem was corrected. Post-incident learning should state learning status, root-cause profile, recurrence-risk class, corrective action, preventive action, verification evidence, affected artifacts, steward or declined responsibility, residual risk, and reopen trigger before the archive claims that the pattern is understood, contained, or less likely to recur.

### Bet 93: Learned controls need monitoring, effectiveness evidence, and sunset rules

A satisfactory research archive should not treat a learned control, validation check, warning, deployment boundary, source-dependent limit, or post-incident preventive action as durable merely because it was verified once. Monitoring should state monitoring status, effectiveness class, residual-risk trend, review trigger, owner or declined responsibility, escalation path, and sunset/renewal condition before the archive claims that a control remains effective, should be retired, or no longer requires attention.

### Bet 94: Individually bounded risks can still form a fragile portfolio

A satisfactory research archive should not infer collective safety from individually acceptable risks. Portfolio review should state which debts, controls, warnings, source dependencies, derivative permissions, deployment boundaries, incident patterns, monitoring obligations, validation checks, and stewardship duties are being aggregated; what dependencies and common-cause failures they share; where cumulative review or source-refresh burden is accumulating; what priority treatment follows; and what claim language remains forbidden.

### Bet 95: Priority is not capacity

A satisfactory research archive should not treat a red flag, high-priority label, release debt, backlog line, owner name, review trigger, or future schedule as proof that work is actually resourced. Capacity review should state capacity status, backlog-admission class, work-in-progress class, deferral/resource-debt class, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed claim language, forbidden claim language, and open capacity debt before a priority item is described as assigned, scheduled, manageable, monitored, safe to defer, or handled.

### Bet 96: Rows before rhetoric

A satisfactory research archive should not treat a schema, register, validation transcript, control sequence, cube metaphor, source crosswalk, or query claim as machine-readable governance evidence until the relevant row type, schema profile, required-field result, control-stack position, dimensions, measures, attributes, allowed query class, forbidden inference, and open conformance debt have been stated.

## How to use the archive

Start with:

1. `01-working-synthesis-layered-process-realism.md`
2. `03-method-selection-and-compression-rules.md`
3. `06-kernel-operators.md`
4. `08-dependence-relations-map.md`
5. `10-laws-powers-and-structure.md`
6. `12-unity-sortals-and-persistence.md`
7. `13-truthmakers-absences-and-privation.md`
8. `14-properties-universals-tropes-and-kinds.md`
9. `15-essence-possibility-and-necessity.md`
10. `16-category-discipline-objects-events-facts-relations.md`
11. `17-mereology-composition-and-boundaries.md`
12. `18-causation-production-counterfactuals-and-intervention.md`
13. `19-time-change-tense-and-passage.md`
14. `20-space-place-location-and-co-location.md`
15. `21-being-existence-and-ontological-commitment.md`
16. `22-teleology-function-and-directedness.md`
17. `23-abstracta-propositions-numbers-and-structures.md`
18. `24-potentiality-actuality-and-actualization.md`
19. `25-relations-internality-externality-and-holism.md`
20. `26-levels-scales-and-cross-level-explanation.md`
21. `27-vagueness-indeterminacy-and-borderline-ontology.md`
22. `28-substance-bearers-and-substrata.md`
23. `29-identity-individuality-and-haecceity.md`
24. `30-naturalness-joint-carving-and-ontic-selectivity.md`
25. `31-determinables-determinates-and-explanatory-grain.md`
26. `32-supervenience-realization-and-modal-covariance.md`
27. `33-well-foundedness-loops-and-architectural-direction.md`
28. `34-nonexistents-fiction-and-merely-possible-objects.md`
29. `35-constitution-coincidence-and-material-constitution.md`
30. `36-things-stuff-fields-and-distributed-being.md`
31. `37-social-ontology-status-functions-and-institutional-reality.md`
32. `38-information-representation-and-aboutness.md`
33. `39-symmetry-invariance-and-surplus-structure.md`
34. `40-chance-probability-and-objective-uncertainty.md`
35. `41-continuity-discreteness-and-granularity.md`
36. `42-indexicality-self-location-and-centered-reality.md`
37. `43-agency-control-and-self-governance.md`
38. `44-normativity-reasons-and-deontic-structure.md`
39. `45-persons-selves-and-first-personal-subjects.md`
40. `46-life-organisms-and-living-form.md`
41. `47-consciousness-experience-and-phenomenal-subjectivity.md`
42. `48-fundamentality-grounding-and-metaphysical-explanation.md`
43. `49-matter-form-and-hylomorphic-organization.md`
44. `50-processes-activities-and-becoming.md`
45. `51-worldhood-totality-and-priority-monism.md`
46. `52-appearance-manifestation-and-the-manifest-image.md`
47. `53-organization-constraints-and-mechanisms.md`
48. `54-powers-dispositions-abilities-and-manifestation.md`
49. `55-structure-patterns-networks-and-relational-constitution.md`
50. `56-facts-states-of-affairs-and-obtaining.md`
51. `57-truth-correspondence-and-reality-answerability.md`
52. `58-ontological-status-robustness-and-derivative-reality.md`
53. `59-objectivity-mind-independence-and-response-dependence.md`
54. `60-indispensability-representation-and-ontological-promotion.md`
55. `61-measurement-detection-and-operationalization.md`
56. `62-directness-mediation-and-world-contact.md`
57. `63-evidence-confirmation-and-underdetermination.md`
58. `64-abduction-explanatory-virtues-and-ontological-inference.md`
59. `65-robustness-triangulation-and-convergent-access.md`
60. `66-artifact-risk-distortion-and-failure-modes.md`
61. `67-access-architecture-disclosure-correction-and-ontological-discipline.md`
62. `68-reference-designation-and-target-fixation.md`
63. `69-ontological-revision-retention-and-elimination.md`
64. `70-contrast-classes-rival-carvings-and-comparative-ontological-choice.md`
65. `71-idealization-approximation-and-limit-cases.md`
66. `72-equivalence-reformulation-and-duality.md`
67. `73-regimes-domains-and-scope-conditions.md`
68. `74-metametaphysics-substantiveness-verbalism-and-worldly-difference.md`
69. `75-autonomy-closure-self-maintenance-and-self-governance.md`
70. `76-scaffolding-support-niche-construction-and-environmental-enablement.md`
71. `77-porous-boundaries-selective-exchange-and-regulated-openness.md`
72. `78-repair-resilience-plasticity-and-adaptive-reorganization.md`
73. `79-dormancy-latency-standby-and-suspended-activity.md`
74. `80-delegation-proxying-handoff-and-distributed-enactment.md`
75. `81-malfunction-pathology-deviance-and-misfire.md`
76. `82-masking-inhibition-suppression-and-blocked-manifestation.md`
77. `83-onset-activation-threshold-crossing-and-phase-entry.md`
78. `84-cessation-deactivation-offlining-and-terminal-ending.md`
79. `85-reactivation-recurrence-restart-and-return.md`
80. `86-succession-inheritance-descent-and-lineage-continuity.md`
81. `87-duplication-copying-fission-and-branching-continuity.md`
82. `88-fusion-merger-coalescence-and-convergent-unity.md`
83. `89-overlap-shared-parts-interpenetration-and-partial-commonality.md`
84. `90-exclusion-incompatibility-occupancy-limits-and-mutual-blocking.md`
85. `91-counteraction-cancellation-neutralization-and-net-suppression.md`
86. `92-overdetermination-redundancy-backup-and-failover.md`
87. `93-amplification-synergy-catalysis-and-positive-feedback.md`
88. `94-negative-feedback-buffering-homeostasis-and-stabilizing-control.md`
89. `95-synchronization-entrainment-rhythm-and-phase-locking.md`
90. `96-desynchronization-phase-drift-phase-slip-and-decoherence.md`
91. `97-gating-coupling-tuning-and-selective-responsiveness.md`
92. `98-saturation-overload-refractory-periods-and-capacity-limits.md`
93. `99-habituation-sensitization-desensitization-and-response-recalibration.md`
94. `100-attractors-basins-metastability-and-landscape-constraint.md`
95. `101-history-sensitivity-traces-records-and-sedimented-constraint.md`
96. `102-critical-transitions-bifurcation-resilience-loss-and-landscape-reorganization.md`
97. `103-attrition-wear-fatigue-degradation-and-reserve-erosion.md`
98. `104-irreversibility-hysteresis-ratcheting-and-return-asymmetry.md`
99. `105-fragility-brittleness-vulnerability-and-cascade-susceptibility.md`
100. `106-compartmentalization-modularity-insulation-and-firebreaks.md`
101. `107-delay-lag-aftereffect-and-temporal-decoupling.md`
102. `108-inertia-momentum-coasting-and-overshoot.md`
103. `109-friction-drag-viscosity-impedance-and-dissipative-resistance.md`
104. `110-elasticity-compliance-strain-storage-and-prestressed-potential.md`
105. `111-slack-tolerance-bands-deadband-backlash-and-clearance.md`
106. `112-interference-noise-crosstalk-and-parasitic-coupling.md`
107. `113-attenuation-filtering-screening-and-shielding.md`
108. `114-sequestration-binding-trapping-and-selective-retention.md`
109. `115-release-discharge-unloading-and-mobilization.md`
110. `116-leakage-seepage-permeation-and-uncontrolled-escape.md`
111. `117-accumulation-pooling-deposition-and-localized-buildup.md`
112. `118-depletion-drawdown-consumption-and-stock-exhaustion.md`
113. `119-replenishment-recharge-restocking-and-stock-reconstitution.md`
114. `120-turnover-renewal-exchange-and-constituent-cycling.md`
115. `121-circulation-throughput-recirculation-and-organized-throughflow.md`
116. `122-bottlenecks-congestion-backpressure-and-chokepoints.md`
117. `123-rerouting-diversion-bypass-and-shunting.md`
118. `124-substitution-replacement-stand-ins-and-functional-equivalence.md`
119. `125-migration-transplantation-porting-and-redeployment.md`
120. `126-hosting-lodging-carriage-and-guest-occupancy.md`
121. `127-attachment-anchoring-tethering-mooring-and-docking.md`
122. `128-embedding-insertion-implantation-and-insetting.md`
123. `129-enclosure-encasement-casing-housing-and-encapsulation.md`
124. `130-coating-cladding-lining-surfacing-and-veneering.md`
125. `131-wrapping-sheathing-draping-shrouding-and-bandaging.md`
126. `132-lamination-interleaving-sandwiching-and-stratified-stacking.md`
127. `133-sealing-closure-plugging-gasketing-and-caulking.md`
128. `134-joining-bonding-welding-brazing-and-soldering.md`
129. `135-articulation-hinging-pivoting-and-socketed-coupling.md`
130. `136-clamping-compression-locking-cinching-crimping-and-press-fit-retention.md`
131. `137-latching-capture-keying-detents-and-positive-lock-engagement.md`
132. `138-threading-screwing-bolting-nutting-and-helical-fastening.md`
133. `139-meshing-gearing-splining-interdigitation-and-toothed-engagement.md`
134. `140-gripping-traction-friction-drive-and-slip-limited-engagement.md`
135. `141-support-bearing-suspension-hanging-bracing-and-load-path-carriage.md`
136. `142-guiding-channeling-conduiting-ducting-and-rail-guided-passage.md`
137. `143-valving-throttling-metering-and-aperture-control.md`
138. `144-operator-family-map-and-triage-grid.md`
139. `145-adversarial-stress-tests-and-revision-protocol.md`
140. `146-diagnostic-case-ledger-calibration-set-and-benchmark-protocol.md`
141. `147-revision-dependency-graph-update-propagation-and-drift-control.md`
142. `148-terminology-register-synonym-control-and-crosswalk-protocol.md`
143. `149-claim-status-register-maturity-levels-and-commitment-governance.md`
144. `150-application-dossier-decision-record-and-verdict-report-protocol.md`
145. `151-precedent-reuse-appeal-transfer-and-review-governance.md`
146. `152-transmission-excerpt-compression-and-pedagogical-governance.md`
147. `153-reception-feedback-errata-and-correction-loop-governance.md`
148. `154-release-gates-maintenance-ledgers-deprecation-and-rollback-governance.md`
149. `155-version-lineage-compatibility-forking-and-migration-governance.md`
150. `156-provenance-custody-build-evidence-and-reproducibility-governance.md`
151. `157-review-authority-audit-certification-and-claim-warrant-governance.md`
152. `158-public-reliance-citation-dispute-withdrawal-and-retraction-governance.md`
153. `159-stewardship-obligations-delegated-authority-and-accountability-governance.md`
154. `160-operational-registers-watch-queues-and-continuity-memory-governance.md`
155. `161-validation-harness-invariant-checks-and-machine-readable-governance.md`
156. `162-release-workflow-runbooks-execution-traces-and-handoff-governance.md`
157. `163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md`
158. `164-semantic-fidelity-generated-output-audit-and-warning-retention-governance.md`
159. `165-operational-reliance-deployment-boundaries-and-action-use-governance.md`
160. `166-incident-response-harm-review-near-miss-and-recovery-governance.md`
161. `167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md`
162. `168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md`
163. `169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md`
164. `170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md`
165. `171-schema-conformance-datacube-control-stack-and-queryable-governance.md`

Operational validation, workflow, automation, semantic-fidelity, deployment-boundary, incident-response, post-incident learning, effectiveness-monitoring, risk-portfolio, capacity-allocation, schema-conformance, control-stack, and datacube artifacts now include:

- `REGISTERS/README.md`
- `REGISTERS/schemas/validation-record-v1.yml`
- `REGISTERS/schemas/workflow-run-record-v1.yml`
- `REGISTERS/schemas/automation-boundary-record-v1.yml`
- `REGISTERS/schemas/semantic-fidelity-record-v1.yml`
- `REGISTERS/schemas/deployment-boundary-record-v1.yml`
- `REGISTERS/schemas/incident-response-record-v1.yml`
- `REGISTERS/schemas/post-incident-learning-record-v1.yml`
- `REGISTERS/schemas/effectiveness-monitoring-record-v1.yml`
- `REGISTERS/schemas/risk-portfolio-record-v1.yml`
- `REGISTERS/schemas/capacity-allocation-record-v1.yml`
- `CONTROL_STACK.yml`
- `CUBE_INDEX.yml`
- `EXTERNAL_CROSSWALK.yml`
- `REGISTERS/schemas/schema-conformance-report-v1.yml`
- `REGISTERS/schemas/control-stack-record-v1.yml`
- `REGISTERS/schemas/datacube-index-record-v1.yml`
- `REGISTERS/rev0156-release-validation.yml`
- `REGISTERS/rev0156-release-workflow.yml`
- `REGISTERS/rev0157-release-validation.yml`
- `REGISTERS/rev0157-release-workflow.yml`
- `REGISTERS/rev0157-automation-boundary.yml`
- `REGISTERS/rev0158-release-validation.yml`
- `REGISTERS/rev0158-release-workflow.yml`
- `REGISTERS/rev0158-automation-boundary.yml`
- `REGISTERS/rev0158-semantic-fidelity.yml`
- `REGISTERS/rev0159-release-validation.yml`
- `REGISTERS/rev0159-release-workflow.yml`
- `REGISTERS/rev0159-automation-boundary.yml`
- `REGISTERS/rev0159-semantic-fidelity.yml`
- `REGISTERS/rev0159-deployment-boundary.yml`
- `REGISTERS/rev0160-release-validation.yml`
- `REGISTERS/rev0160-release-workflow.yml`
- `REGISTERS/rev0160-automation-boundary.yml`
- `REGISTERS/rev0160-semantic-fidelity.yml`
- `REGISTERS/rev0160-deployment-boundary.yml`
- `REGISTERS/rev0160-incident-response.yml`
- `REGISTERS/rev0161-release-validation.yml`
- `REGISTERS/rev0161-release-workflow.yml`
- `REGISTERS/rev0161-automation-boundary.yml`
- `REGISTERS/rev0161-semantic-fidelity.yml`
- `REGISTERS/rev0161-deployment-boundary.yml`
- `REGISTERS/rev0161-incident-response.yml`
- `REGISTERS/rev0161-post-incident-learning.yml`
- `REGISTERS/rev0162-release-validation.yml`
- `REGISTERS/rev0162-release-workflow.yml`
- `REGISTERS/rev0162-automation-boundary.yml`
- `REGISTERS/rev0162-semantic-fidelity.yml`
- `REGISTERS/rev0162-deployment-boundary.yml`
- `REGISTERS/rev0162-incident-response.yml`
- `REGISTERS/rev0162-post-incident-learning.yml`
- `REGISTERS/rev0162-effectiveness-monitoring.yml`
- `REGISTERS/rev0163-release-validation.yml`
- `REGISTERS/rev0163-release-workflow.yml`
- `REGISTERS/rev0163-automation-boundary.yml`
- `REGISTERS/rev0163-semantic-fidelity.yml`
- `REGISTERS/rev0163-deployment-boundary.yml`
- `REGISTERS/rev0163-incident-response.yml`
- `REGISTERS/rev0163-post-incident-learning.yml`
- `REGISTERS/rev0163-effectiveness-monitoring.yml`
- `REGISTERS/rev0163-risk-portfolio.yml`
- `REGISTERS/rev0164-release-validation.yml`
- `REGISTERS/rev0164-release-workflow.yml`
- `REGISTERS/rev0164-automation-boundary.yml`
- `REGISTERS/rev0164-semantic-fidelity.yml`
- `REGISTERS/rev0164-deployment-boundary.yml`
- `REGISTERS/rev0164-incident-response.yml`
- `REGISTERS/rev0164-post-incident-learning.yml`
- `REGISTERS/rev0164-effectiveness-monitoring.yml`
- `REGISTERS/rev0164-risk-portfolio.yml`
- `REGISTERS/rev0164-capacity-allocation.yml`
- `REGISTERS/rev0166-release-validation.yml`
- `REGISTERS/rev0166-release-workflow.yml`
- `REGISTERS/rev0166-automation-boundary.yml`
- `REGISTERS/rev0166-semantic-fidelity.yml`
- `REGISTERS/rev0166-deployment-boundary.yml`
- `REGISTERS/rev0166-incident-response.yml`
- `REGISTERS/rev0166-post-incident-learning.yml`
- `REGISTERS/rev0166-effectiveness-monitoring.yml`
- `REGISTERS/rev0166-risk-portfolio.yml`
- `REGISTERS/rev0166-capacity-allocation.yml`
- `REGISTERS/rev0166-schema-conformance.yml`
- `REGISTERS/rev0166-control-stack.yml`
- `REGISTERS/rev0166-datacube-index.yml`
- `RUNBOOKS/release-workflow-v1.md`
- `RUNBOOKS/automation-delegation-v1.md`
- `RUNBOOKS/semantic-fidelity-review-v1.md`
- `RUNBOOKS/deployment-boundary-review-v1.md`
- `RUNBOOKS/incident-response-review-v1.md`
- `RUNBOOKS/post-incident-learning-review-v1.md`
- `RUNBOOKS/effectiveness-monitoring-review-v1.md`
- `RUNBOOKS/risk-portfolio-review-v1.md`
- `RUNBOOKS/capacity-allocation-review-v1.md`
- `RUNBOOKS/schema-conformance-datacube-review-v1.md`
- `tools/validate_archive.py`

Use `02-comparative-map-of-live-options.md` to keep rivals active, `04-open-questions-and-discriminating-tests.md` to decide where the next revision should go, `144-operator-family-map-and-triage-grid.md` to route candidate additions before expanding the archive, `145-adversarial-stress-tests-and-revision-protocol.md` to attack the preferred routing before stabilizing a verdict, `146-diagnostic-case-ledger-calibration-set-and-benchmark-protocol.md` to record reusable hard cases as calibration instruments rather than anecdotes, `147-revision-dependency-graph-update-propagation-and-drift-control.md` to ensure accepted changes have propagated, been explicitly declined, or been ledgered as open debt before packaging the next revision, `148-terminology-register-synonym-control-and-crosswalk-protocol.md` to keep canonical terms, aliases, source terms, metaphors, and unsafe shortcuts from doing unearned operator-work, `149-claim-status-register-maturity-levels-and-commitment-governance.md` to keep kernel commitments, working defaults, diagnostics, calibrated precedents, domain-local rules, live rivals, provisional probes, quarantines, source-dependent commitments, deprecated items, and open debts from being confused, `150-application-dossier-decision-record-and-verdict-report-protocol.md` to turn reusable verdicts into auditable decision records rather than free-floating conclusions, `151-precedent-reuse-appeal-transfer-and-review-governance.md` to govern when those decision records may be reused, taught, transferred, appealed, superseded, or marked do-not-reuse, `152-transmission-excerpt-compression-and-pedagogical-governance.md` to govern how allowed material may be summarized, excerpted, diagrammed, taught, or exported without losing its limits, `153-reception-feedback-errata-and-correction-loop-governance.md` to classify downstream uptake, misunderstanding, criticism, errata, operational failure, teaching drift, source-boundary failure, and package-drift signals before feedback is allowed to revise doctrine, `154-release-gates-maintenance-ledgers-deprecation-and-rollback-governance.md` to classify release type, gate outcomes, open debt, deprecation, migration, hotfix, rollback, source implication, and verification status before a package is treated as complete, `155-version-lineage-compatibility-forking-and-migration-governance.md` to classify version identity, lineage relation, compatibility class, fork status, migration rule, merge rule, allowed reuse, forbidden reuse, and open lineage debt before archive material is cited, forked, migrated, merged, taught, or retained across versions, `156-provenance-custody-build-evidence-and-reproducibility-governance.md` to classify claimed version identity, source artifact, custody path, edit intent, transformations, touched files, generated material, verification evidence, reproducibility status, tamper signals, allowed trust, and provenance debt before an artifact is trusted, imported, recovered, rebuilt, cited, or handed off, `157-review-authority-audit-certification-and-claim-warrant-governance.md` to classify reviewer role, authority basis, independence status, review scope, evidence inspected, findings, certification status, allowed wording, forbidden wording, conflicts, expiry triggers, and return path before a result is called reviewed, audited, certified, validated, approved, source-reviewed, externally reviewed, or release-warranted, and `158-public-reliance-citation-dispute-withdrawal-and-retraction-governance.md` to classify public-use status, intended audience, permitted use, forbidden use, required warnings, citation form, dispute path, update/notice path, expiry trigger, and withdrawal or retraction rule before a reviewed or released result is allowed to function as a public reliance object, `159-stewardship-obligations-delegated-authority-and-accountability-governance.md` to classify steward role, authority basis, obligation class, accepted and declined duties, delegation or handoff, update/watch trigger, warning duty, correction path, high-stakes boundary, and accountability consequence before a public or derivative use is treated as responsibly stewarded, and `160-operational-registers-watch-queues-and-continuity-memory-governance.md` to classify register type, controlling packets, responsible role, continuity status, watch trigger, notice path, closure evidence, open continuity debt, and successor-memory field before an accepted duty is treated as operationally maintained.

Finally, use `161-validation-harness-invariant-checks-and-machine-readable-governance.md` to classify validation status, invariant family, failure severity, schema/checklist scope, local-machine-readable status, and automation boundary before claiming that a release, packet, register, fork, derivative, or public artifact is validation-backed, machine-checkable, dashboard-ready, or operationally monitored.

Then use `162-release-workflow-runbooks-execution-traces-and-handoff-governance.md` to classify workflow status, runbook identity, stage order, entry and exit criteria, evidence artifacts, validation point, manifest/package point, fresh-extraction result, skipped stages, exception handling, handoff limits, allowed wording, forbidden wording, open workflow debt, and next workflow trigger before claiming that a release is workflow-controlled, runbook-executed, handoff-ready, repeatably produced, or successor-readable.

Then use `163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md` to classify automation status, tool-permission class, scheduled-execution class, authorized scope, prohibited scope, human-review gate, evidence artifacts, allowed wording, forbidden wording, stop conditions, and open automation debt before claiming that a release, derivative, validation, source watch, generated output, public handoff, or scheduled task is automated, agent-assisted, monitored, independently re-executed, source-current, or tool-certified.

Then use `164-semantic-fidelity-generated-output-audit-and-warning-retention-governance.md` to classify semantic-fidelity status, warning-retention class, source version, output type, compression level, target/basis/status/non-verdict/source/version fidelity, warnings retained, warnings omitted, allowed reuse, forbidden reuse, and next fidelity trigger before claiming that a summary, diagram, table, generated answer, teaching handout, source digest, derivative excerpt, or release note is faithful to the archive.

Finally, use `docs/165-operational-reliance-deployment-boundaries-and-action-use-governance.md` to classify deployment status, action-reliance class, operational context, affected parties, domain/source-current review, human-review gate, override path, notice/dispute/appeal path, correction/rollback path, monitoring requirement, permitted actions, forbidden actions, incident triggers, and open deployment debt before claiming that a summary, teaching handout, generated answer, derivative artifact, public note, register, workflow, or archive-derived classifier is policy-ready, procedure-ready, decision-support-ready, automation-ready, institutionally deployable, or high-stakes operational guidance.

Then use `docs/166-incident-response-harm-review-near-miss-and-recovery-governance.md` to classify incident status, harm/severity class, recovery class, affected scope, evidence preserved, containment action, notice path, correction/rollback/withdrawal path, residual risk, closure evidence, and successor-memory trigger when archive-derived action-use, attempted action-use, public reliance, derivative reuse, automation, or deployment-boundary failure produces a harmful or recovery-relevant event.

Finally, use `docs/167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md` to classify learning status, root-cause profile, recurrence-risk class, corrective action, preventive action, verification evidence, affected artifacts, residual risk, and reopen trigger before claiming that a recovered incident, near miss, warning failure, derivative misuse, public-reliance failure, or deployment-boundary failure has been learned rather than merely patched.

Then use `docs/168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md` to classify monitoring status, effectiveness class, residual-risk trend, evidence basis, review trigger, owner or declined responsibility, escalation route, and sunset/renewal class before claiming that a learned control, warning, validation check, deployment boundary, source-dependent limit, derivative restriction, release gate, or post-incident preventive action remains effective, is actively monitored, should be renewed, or can be safely retired.

Finally, use `docs/169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed claim language, forbidden claim language, owner or declined responsibility, and next review trigger before claiming that a collection of risks, controls, open debts, source dependencies, derivative permissions, deployment boundaries, incidents, learning packets, monitoring packets, validation checks, or stewardship obligations is collectively manageable, low risk, accepted, or safe to defer.

Then use `docs/170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` to classify capacity status, backlog-admission class, work-in-progress class, deferral/resource-debt class, resource basis, scarce dependency, owner or declined responsibility, next action, review window, WIP limit, stop condition, allowed claim language, forbidden claim language, and open capacity debt before claiming that a priority item, queue, source-refresh need, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation is assigned, scheduled, manageable, monitored, safe to defer, or handled.
Then use `docs/171-schema-conformance-datacube-control-stack-and-queryable-governance.md` to classify schema-conformance status, record profile, control-stack status, datacube-readiness status, query-permission class, row type, dimensions, measures, attributes, required-field result, allowed query language, forbidden inference, and open conformance debt before claiming that a register, control sequence, validation result, source crosswalk, cube index, or release packet is queryable, cube-ready, schema-conformant, control-map-consistent, or machine-readable in any strong sense.


Rev0165 schema/datacube front-door artifacts: `EXTERNAL_CROSSWALK.yml`, `RUNBOOKS/schema-conformance-datacube-review-v1.md`, `REGISTERS/schemas/schema-conformance-report-v1.yml`, `REGISTERS/schemas/control-stack-record-v1.yml`, `REGISTERS/schemas/datacube-index-record-v1.yml`, `REGISTERS/rev0166-schema-conformance.yml`, `CONTROL_STACK.yml`, `CUBE_INDEX.yml`, and `tools/query_cube.py`.

Rev0165 standalone conformance report: `REGISTERS/schema-conformance-report-rev0166.yml`.


## Rev0166 start-here note

Bet 97: A cube is only as stable as its vocabulary, references, query regressions, claim language, and provenance boundaries.

Use `docs/172-status-vocabulary-reference-integrity-query-regression-claim-language-and-provenance-governance.md` after doc 171 whenever a new status token, local path reference, query boundary, public-use claim, or provenance claim is introduced.

Rev0166 front-door artifacts: `STATUS_VOCABULARY.yml`, `REFERENCE_MAP.yml`, `QUERY_REGRESSION_SUITE.yml`, `CLAIM_LANGUAGE_LEDGER.yml`, `PROVENANCE_LEDGER.yml`, `tools/check_reference_integrity.py`, and `tools/run_query_regression.py`.

## Rev0167 addendum: invariants, traceability, change impact, migration, and fixtures

Final numbered document: `docs/173-invariant-catalog-traceability-matrix-change-impact-migration-and-fixture-governance.md`.

New required artifacts: `INVARIANT_CATALOG.yml`, `TRACEABILITY_MATRIX.yml`, `CHANGE_IMPACT_MATRIX.yml`, `MIGRATION_LEDGER.yml`, `FIXTURE_CORPUS.yml`, `RUNBOOKS/invariant-traceability-migration-fixture-review-v1.md`, `tools/check_invariants.py`, `tools/check_traceability.py`, and `tools/run_fixture_corpus.py`.

The package may claim local invariant cataloging, local traceability rows, local change-impact recording, local migration/deprecation classification, local representative fixture pressure, local current-record/schema/status/reference/query/provenance checks, and fresh-extraction validator success. It must not claim formal verification, semantic truth validation, exhaustive QA, public CI, public issue tracking, Semantic Versioning compliance, OpenLineage emission, Great Expectations deployment, ODRL publication, external audit, source currency, domain review, or operational readiness.


## Rev0168 addendum: claim graph, evidence packets, contradiction, freshness, and defeasance

Use `docs/174-claim-graph-evidence-packets-contradiction-freshness-and-defeasance-governance.md` after doc 173 whenever a package claim, evidence packet, contradiction state, freshness rule, or downstream defeasance rule is introduced or revised.

Rev0168 front-door artifacts: `CLAIM_GRAPH.yml`, `EVIDENCE_PACKET_INDEX.yml`, `CONTRADICTION_LEDGER.yml`, `FRESHNESS_POLICY.yml`, `DEFEASANCE_PROPAGATION.yml`, `RUNBOOKS/claim-evidence-defeasance-review-v1.md`, `tools/check_claim_evidence.py`, `REGISTERS/claim-graph-report-rev0168.yml`, `REGISTERS/evidence-packet-report-rev0168.yml`, `REGISTERS/contradiction-report-rev0168.yml`, `REGISTERS/freshness-report-rev0168.yml`, and `REGISTERS/defeasance-report-rev0168.yml`.

Bet 98: a claim is not release-safe merely because it appears in a validated package; it must name its warrant, freshness window, contradiction state, and defeat propagation path.


## Rev0169 addendum: release gate policy, acceptance criteria, decisions, waivers, risk acceptance, and assurance case skeleton

Use `docs/175-release-gate-policy-acceptance-criteria-risk-acceptance-and-assurance-case-governance.md` after doc 174 whenever a local release claim, package handoff, risk acceptance, waiver/exception, gate pass, gate failure, or assurance-case claim is introduced or revised.

Rev0169 front-door artifacts: `RELEASE_GATE_POLICY.yml`, `ACCEPTANCE_CRITERIA_MATRIX.yml`, `RELEASE_DECISION_LEDGER.yml`, `WAIVER_EXCEPTION_LEDGER.yml`, `RISK_ACCEPTANCE_LEDGER.yml`, `ASSURANCE_CASE_SKELETON.yml`, `RUNBOOKS/release-gate-decision-assurance-review-v1.md`, `tools/check_release_gates.py`, `REGISTERS/release-gate-report-rev0169.yml`, `REGISTERS/acceptance-criteria-report-rev0169.yml`, `REGISTERS/release-decision-report-rev0169.yml`, `REGISTERS/waiver-exception-report-rev0169.yml`, `REGISTERS/risk-acceptance-report-rev0169.yml`, and `REGISTERS/assurance-case-report-rev0169.yml`.

Bet 99: release safety is not established by a validated package alone; release requires named gates, acceptance criteria, waiver treatment, residual-risk boundaries, decision records, and an assurance case skeleton.


## Rev0170 update: reproducibility, attestation boundary, custody, execution log, rollback, and public-release packet governance

Rev0170 adds `docs/176-reproducibility-attestation-evidence-chain-custody-rollback-and-public-release-boundary-governance.md`, `BUILD_REPRODUCIBILITY_LEDGER.yml`, `ATTESTATION_BOUNDARY_LEDGER.yml`, `EVIDENCE_CHAIN_CUSTODY.yml`, `EXECUTION_LOG_LEDGER.yml`, `ROLLBACK_RETRACTION_PLAN.yml`, `PUBLIC_RELEASE_ATTESTATION.yml`, and `tools/check_repro_attestation.py`.

The new layer records a local build recipe, explicit unsigned-attestation boundary, package-internal evidence custody rows, local execution-log expectations, rollback/retraction triggers, and a bounded public-release packet. It does not claim bit-for-bit reproducibility, hermetic builds, independent rebuild, signed provenance, SLSA level, Sigstore/cosign signature, in-toto attestation, SCITT transparency receipt, legal chain of custody, public CI, external approval, operational deployment readiness, or source-current/domain-authoritative review.

## Rev0171 post-release observability, audit, feedback, reliance, drift, and exercise layer

Current final document: `docs/177-post-release-observability-audit-sampling-feedback-reliance-drift-and-exercise-governance.md`.

New current-release artifacts: `OBSERVABILITY_MONITORING_PLAN.yml`, `AUDIT_SAMPLING_PLAN.yml`, `FEEDBACK_INTAKE_LEDGER.yml`, `DOWNSTREAM_RELIANCE_LEDGER.yml`, `DRIFT_ANOMALY_LEDGER.yml`, `EXERCISE_INCIDENT_DRILL_LEDGER.yml`, and `tools/check_observability_feedback.py`.

Rev0171 keeps rev0170's unsigned/local attestation boundary and adds post-release accountability surfaces. It does not claim public monitoring, public support, continuous telemetry, downstream recall authority, independent audit, legal attestation, or operational deployment readiness.

## Rev0172 remediation, severity, local objectives, corrective action, escalation, and closure layer

Current final document: `docs/178-remediation-triage-severity-service-objectives-corrective-action-escalation-and-closure-governance.md`.

New current-release artifacts: `REMEDIATION_TRIAGE_POLICY.yml`, `SEVERITY_CLASSIFICATION_MATRIX.yml`, `SERVICE_OBJECTIVE_LEDGER.yml`, `CORRECTIVE_ACTION_REGISTER.yml`, `COMMUNICATION_ESCALATION_LEDGER.yml`, `CLOSURE_VERIFICATION_LEDGER.yml`, `RUNBOOKS/remediation-triage-corrective-action-closure-review-v1.md`, and `tools/check_remediation_closure.py`.

Rev0172 keeps rev0171's post-release observability boundary and adds local remediation accountability. It does not claim public support, service-level commitments, legal incident response, external notification duty, public recall authority, independently audited remediation, or operational deployment readiness.


## Rev0173 addition — accountability and authority governance

This revision adds `docs/179-role-authority-accountability-assignment-segregation-delegation-approval-and-review-governance.md` plus the local accountability surfaces `ROLE_AUTHORITY_MATRIX.yml`, `ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml`, `SEGREGATION_OF_DUTIES_POLICY.yml`, `DELEGATION_HANDOFF_LEDGER.yml`, `APPROVAL_CONSENT_LEDGER.yml`, `ACCOUNTABILITY_REVIEW_LEDGER.yml`, `RUNBOOKS/accountability-authority-review-v1.md`, and `tools/check_accountability_authority.py`.  The added layer prevents local role labels, assignment rows, approvals, warnings, handoffs, and delegated execution from being upgraded into external review, public consent, legal authority, public support, or operational deployment permission.


Rev0180 accessibility/comprehension layer: see `docs/186-accessibility-readability-discoverability-localization-onboarding-and-inclusive-access-governance.md` and `ACCESSIBILITY_REVIEW_PLAN.yml`.

## rev0184 note

Current package: `Metaphysics-rev0185-2026.05.26.05.18-debt-cube-lifecycle-prioritization-audit-refactor.zip`. Current layer: `docs/190-claim-cube-warrant-defeasance-contradiction-audit-governance.md`. The layer adds local ClaimCube observation, relation, and audit surfaces without claiming external audit, claim truth, complete contradiction detection, automatic truth maintenance, RDF/SHACL publication, or philosophical completeness.



## Current rev0185 orientation

For the newest layer, start with `docs/191-debt-cube-lifecycle-prioritization-remediation-audit-governance.md`. It refactors the DebtCube as lifecycle/priority/relation/audit observations without claiming closure or owner assignment.
