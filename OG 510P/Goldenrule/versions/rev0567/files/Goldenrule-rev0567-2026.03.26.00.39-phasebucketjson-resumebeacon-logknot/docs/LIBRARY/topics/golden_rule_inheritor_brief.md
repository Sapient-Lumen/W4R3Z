# Golden Rule Inheritor Brief

This note is for the next operator who inherits Concord as a live research program rather than a static archive.

## What the archive now says clearly

1. A Golden-Rule-like strategy is not just “cooperate a lot.” It must survive extortion, noise, role asymmetry, and bad information.
2. Dyadic memory-one reciprocity is necessary but not sufficient. The frontier now includes longer memory, partner choice, repair channels, reputation, and explicit universalisation baselines.
3. The archive already contains enough evidence to justify moving away from single-number strategy search.

## Local empirical signal worth keeping in mind

The existing extortion-search artifacts point to a metric trap:
- short-horizon search can find candidates that beat extortion on `avg_a`,
- longer random search can maximize `avg_a` while still handing extortion a much larger payoff,
- hill climbing can reduce the payoff gap, but at a cost in self-payoff.

Interpretation: “maximize my score against the vampire” is not the same as “learn a strategy that resists vampirism.”

## Build order I would actually follow

1. Add an anti-vampire scorecard with at least four fields: own payoff, payoff gap, recovery to mutual cooperation after a shock, and repair-channel abuse rate.
2. Add one opt-out / leave-and-rematch world. Partner choice is now strong enough in the literature that it should stop being a prose-only future idea.
3. In that world, separate **observable help** from **hidden partner-maintenance help** so performative cooperation does not count as Golden-Rule progress.
4. Add one minimal reputation lane with an explicit public/private assessment-update rule rather than a vague "reputation on" toggle.
5. In that reputation lane, keep sparse observation separate from fading / `Unknown` reputation states; they are not the same institution.
6. If gossip is enabled, publish cadence / fan-in / trust-weight / merge semantics and keep one no-gossip comparison.
7. Add one small longer-memory family (reactive-2 or recency-weighted memory) instead of jumping straight to open-ended search.
8. Add one explicit universalisation baseline, even if heuristic. The point is comparability, not philosophical completeness.
9. Only after the above, widen search breadth. Otherwise search will optimize the wrong target faster.
10. If the cloudtainer still lacks `cargo` / `junest`, start with `make cloudtainer-shadow-pass`, then use `docs/RUST_SURFACE_INVENTORY.md` for static Rust navigation, do Python shadow work against the declared contracts, and leave runtime-semantic claims parked behind the blocked Rust lane instead of burning the session on setup churn.

## New external signal worth carrying forward

- `RS-GR-132` suggests that once leaving under error is real, classical retaliatory winners can disappear and leave-based sanctioning can take over.
- `RS-GR-133` suggests that move order and current-action visibility can preserve some simple memory-one equilibria but destabilize richer ones, so simultaneous and disclosed-action lanes should not be pooled casually.
- `RS-GR-134` suggests that partner choice can increase **visible** reciprocity while decreasing **hidden** partner-maintenance help, so one cooperation scalar is not enough in leave/rematch worlds.
- `RS-GR-135` suggests that in private-reputation settings, cooperation depends materially on the assessment-update rule, so "reputation enabled" is not yet a scientific world description.
- `RS-GR-136` suggests that sparse observation and fading / `Unknown` reputations should not be collapsed: they change cooperation and punishment differently.
- `RS-GR-137` suggests that gossip can stabilize private-reputation worlds, but only under explicit cadence / trust / aggregation rules.
- `RS-GR-138` suggests that in exclusion worlds, apology availability and trackability can change reintegration behavior, so punishment and rehabilitation should not be pooled into one sanction label.
- `RS-GR-139` suggests that apology opportunities can raise cooperation and that public/common-knowledge apology can matter at the group level, so repair-channel visibility is part of the institution.
- `RS-GR-140` suggests that expressive signals can act as error-correction channels under indirect reciprocity, especially when errors are frequent.
- `RS-GR-143` and `RS-GR-145` suggest that hybrid human/AI populations are not small perturbations: artificial agents can alter reputation consensus, and reciprocity can weaken once bots enter the network.
- `RS-GR-144` suggests that one AI's failure can spill over to perceptions of all AIs, so reputation scope in hybrid worlds should not be left implicit.
- `RS-GR-146` and `RS-GR-147` suggest that group-level / collective reputation and stereotype fallback are separate institutional choices from individual reputation.
- `RS-GR-148` suggests that universalistic cooperation can lose local reputational reward under intergroup competition.
- `RS-GR-149` suggests that even sparse cross-group mobility can let a minority of agents enforce intergroup cooperation.
- `RS-GR-150` suggests that indirect reciprocity can require sufficient opinion synchronization; fully independent private opinions are not just noisier, they can collapse cooperation.
- `RS-GR-151` suggests that weighting public reputation heavily, especially with friend-and-enemy source mixing, can create polarization / fragmentation dynamics rather than simply improving coordination.
- `RS-GR-152` suggests that centralized social-credit-style scores can reduce trust and cooperation and can keep bias sticky even against contradictory fresh behavior.
- `RS-GR-153` and `RS-GR-154` suggest that trust and reputation results can depend on monitoring cost and evidence-transfer friction, so observation economics should not be hidden as backend plumbing.
- `RS-GR-155` suggests that partner choice depends on both willingness / warmth and ability / competence, with task affordances changing which dimension matters.
- `RS-GR-156` suggests that need and misfortune can trigger blame or devaluation because helping is costly, so recipient burden should not be left implicit.
- `RS-GR-161` and `RS-GR-162` suggest that inequality changes cooperation differently depending on whether it is luck-framed, merit-framed, productivity-based, or aligned with resource advantage.
- `RS-GR-163`, `RS-GR-164`, and `RS-GR-165` suggest that once goods are scarce, allocation rule and allocator authority can drive cooperation and fairness outcomes rather than merely recording them.
- `RS-GR-166`, `RS-GR-167`, and `RS-GR-168` suggest that punishment metanorms — including what observers should do after a violation and whether non-enforcement is blameworthy — are part of the institution rather than local background culture.
- `RS-GR-169`, `RS-GR-170`, and `RS-GR-171` suggest that sanction results depend on how enforcers are monitored, rewarded, protected, or retaliated against, so punishment cannot be modeled only on the target side.
- `RS-GR-172`, `RS-GR-173`, and `RS-GR-175` suggest that promises and commitments are not generic chat: commitment state can change whether pledges work at all and can change how later actions are judged.
- `RS-GR-174` suggests that cheap post-hoc reputation signals can be used dishonestly, so added communication should not automatically count as repair or prosociality.
- `RS-GR-187` suggests that cooperation can rise or fall because people are trying to avoid losses, so gain/loss sign structure should not be left implicit.
- `RS-GR-188` suggests that threshold cooperation is higher when a task is framed as producing a public good than when it is framed as preventing a public bad.
- `RS-GR-189` suggests that delayed collective harm can make participants less cautious until their own payoff turns negative, so damage latency is not harmless realism.
- `RS-GR-190` suggests that threshold uncertainty is especially destructive under weakest-link aggregation, so threshold certainty and aggregation technology should not be pooled into one generic collective-action lane.
- `RS-GR-195` and `RS-GR-198` suggest that private solutions and self-reliance can crowd out shared provision and widen inequality, so private escape routes should not be treated as harmless extra actions.
- `RS-GR-196` suggests that trust context can shift investment from individual toward collective solutions without increasing free-riding, so public/private solution mix is partly an institutional trust problem rather than only a payoff problem.
- `RS-GR-197` suggests that an outside option can help collaboration when groups form flexibly and loner externality is limited, so “outside option present” is not one institution.
- `RS-GR-199` suggests that asking for help is itself a strategic stage: greater need can reduce asking, and the absence of an unsolicited offer can discourage later asking.
- `RS-GR-200` and `RS-GR-201` suggest that request visibility and recognition change the social costs of help-seeking, so help-request audience is not harmless interface flavor.
- `RS-GR-202` suggests that help-seeking norms depend on who adopts the recognition system, so subgroup-asymmetric request recognition should not be left implicit.
- `RS-GR-203` suggests that democratic rule choice can directly change cooperative behavior beyond simple self-selection into preferred rules, so endogenous versus exogenous rule selection should not be left implicit.
- `RS-GR-204` suggests that democratic sanction effects depend on voting scope and sanction design, so “democratic punishment” is not one stable institution.
- `RS-GR-205` suggests that subgroup-binding institutions behave differently from whole-group institutions, so franchise and binding scope should not be collapsed into a yes/no adoption flag.
- `RS-GR-206` suggests that endogeneity is not a universal premium: imposed institutions can outperform chosen ones in some populations.
- `RS-GR-207` suggests that successor-binding commitment mechanisms can raise replenishment and sustainability across generations, so intergenerational lock-in and escape semantics should not be left implicit.
- `RS-GR-208` and `RS-GR-209` suggest that absent future beneficiaries need explicit present-time representation: future design and soft advisory institutions can materially change outcomes even without hard enforcement.
- `RS-GR-210` suggests that future beneficiaries are not a socially neutral target: sustainability shifts when the future beneficiaries are framed as ingroup rather than outgroup.
- `RS-GR-211` suggests that “future generations” is not one flat target: concern and obligation thin out across generational distance, so beneficiary horizon depth should not be left implicit.
- `RS-GR-212`, `RS-GR-213`, and `RS-GR-214` suggest that intertemporal links, psychological proximity, and future-self vividness can materially change future-facing action, but not always in a monotone way, so future vividness and agency should not be left implicit either.
- `RS-GR-215`, `RS-GR-216`, and `RS-GR-217` suggest that future-facing uptake depends not just on outcomes but on how duty is framed and whether latent support for future-generations institutions is made visible, so frame semantics and norm visibility should not be left implicit.
- `RS-GR-218` and `RS-GR-219` suggest that "legacy motivation" is not one thing: impact legacy, reputation legacy, public visibility, and short-lived versus durable salience can separate cleanly in behavior.
- `RS-GR-225` and `RS-GR-226` suggest that future concern is not automatically a tax on present-day solidarity: it can predict costly immediate helping, but willingness also depends on who bears near-term sacrifice and whether present-day beneficiaries are kept in view.
- `RS-GR-227` and `RS-GR-228` suggest that fairness is not one abstract score: support can hinge on whether burdens are evaluated at the household, local-community, vulnerable-subgroup, societal, or future-generational level.
- `RS-GR-229` and `RS-GR-230` suggest that care for one's children or grandchildren is not the same mechanism as care for anonymous future people: descendant-specific framing can widen future concern while also changing household burdens and caregiver constraints.
- `RS-GR-231`, `RS-GR-232`, and `RS-GR-233` suggest that cross-age cooperation depends on who can influence whom and how contact is structured; youth-led dialogue, reciprocal exchange, and stereotype-reducing intergenerational programs are not interchangeable with one-way instruction.
- `RS-GR-234`, `RS-GR-235`, `RS-GR-236`, and `RS-GR-237` suggest that future generations need more than nominal recognition: future design, advisory institutions, and future-regarding scrutiny bodies can alter outcomes by inserting future voice and long-horizon accountability into present decisions.
- `RS-GR-238` and `RS-GR-239` suggest that sustainable-looking solutions can still export burdens across sectors, places, or time or require rolling successor maintenance, so problem-shifting and passive-safety versus stewardship dependence should not be left implicit.
- `RS-GR-240` and `RS-GR-241` suggest that future-facing institutions differ along at least three separable dimensions — seat presence, deliberative depth, and formal teeth — so symbolic inclusion should not be collapsed into empowered future representation.
- `RS-GR-242` and `RS-GR-243` suggest that long-term governance often faces uncertainty about values as well as outcomes, so option-preserving portfolios and ladders can be meaningfully different from optimizing one locked future.
- `RS-GR-244` and `RS-GR-245` suggest that future-facing support depends partly on whether benefits arrive within one's own lifetime and whether personal time horizons have been lengthened, so lifespan-boundary and time-horizon-activation semantics should not be left implicit.
- `RS-GR-246`, `RS-GR-247`, `RS-GR-248`, and `RS-GR-249` suggest that long-horizon protection can operate through hard significant-harm floors, adaptation tipping points, and explicit review / pathway-switch triggers, so threshold and revision-rights semantics should not be left implicit.
- `RS-GR-250`, `RS-GR-251`, `RS-GR-252`, and `RS-GR-253` suggest that future-facing representation depends on who actually speaks for future beneficiaries, how those representatives are selected, and whether cohort composition and diversity are skewed, so proxy-source and selection-route semantics should not be left implicit.
- `RS-GR-254`, `RS-GR-255`, `RS-GR-256`, and `RS-GR-257` suggest that long-horizon institutions differ sharply by permanence, institutional anchoring, recommendation-routing, and cross-cycle memory, so ad-hoc consultation should not be collapsed into durable anticipatory governance.
- `RS-GR-274`, `RS-GR-275`, `RS-GR-276`, and `RS-GR-277` suggest that future protection depends on harm order, reversibility timescale, and limits to substituting or compensating certain losses, so avoidance-first and restoration-order semantics should not be left implicit.
- `RS-GR-278`, `RS-GR-279`, `RS-GR-280`, and `RS-GR-281` suggest that long-horizon prudence can come from robust / adaptive design, no-regret moves, and option preservation under deep uncertainty, so robustness and regret-class semantics should not be collapsed into generic future concern.
- `RS-GR-282`, `RS-GR-283`, and `RS-GR-284` suggest that future-facing prudence can also come from staged commitment, small-scale experimentation, pilot regulation, and delayed lock-in, so pilotability and reversibility semantics should not be collapsed into generic caution or future concern.
- `RS-GR-285`, `RS-GR-286`, and `RS-GR-287` suggest that temporary framing, reauthorization discipline, and policy-stock retirement determine whether obligations actually leave or silently accumulate into overload, so sunset and policy-stock-load semantics should not be left implicit.
- `RS-GR-305`, `RS-GR-306`, `RS-GR-307`, and `RS-GR-308` suggest that long-horizon accountability depends on who can independently verify claims, what evidence and rationale are made public, whether affected outsiders can inspect or challenge, and whether reassessment follows a repeatable protocol, so verification-independence and contestability semantics should not be left implicit.
- `RS-GR-309`, `RS-GR-310`, `RS-GR-311`, and `RS-GR-312` suggest that successor-safe stewardship depends on curated key-information layers, indexed records, renewal and media-migration instructions, and deliberate awareness-preservation strategies, so knowledge-package and renewal-cadence semantics should not be left implicit.
- `RS-GR-351`, `RS-GR-352`, `RS-GR-353`, `RS-GR-354`, `RS-GR-355`, and `RS-GR-356` suggest that long-horizon provenance also depends on retaining compact portable verification packets, knowing which checks survive fully offline, and carrying enough trust-root / re-anchoring state to outlive the original service endpoints, so offline-verification and dependency-survival semantics should not be left implicit.
- `RS-GR-357`, `RS-GR-358`, `RS-GR-359`, `RS-GR-360`, `RS-GR-361`, and `RS-GR-362` suggest that long-horizon provenance also depends on retaining the verifier's rulebook — policy snapshots, accepted roots and identities, claim-check strictness, and deterministic appraisal profile semantics — so future replay does not silently change what a retained proof means.
- `RS-GR-369`, `RS-GR-370`, `RS-GR-371`, `RS-GR-372`, `RS-GR-373`, and `RS-GR-374` suggest that long-horizon provenance also depends on preserving an immutable subject identity for what was signed, logged, or superseded, separating that identity from mutable names / tags / URLs, and keeping alias-to-subject or referrer-to-subject correlation replayable without live resolver trust, so subject-binding and resolver-independence semantics should not be left implicit.

- `RS-GR-375`, `RS-GR-376`, `RS-GR-377`, `RS-GR-378`, `RS-GR-379`, and `RS-GR-380` suggest that long-horizon provenance also depends on preserving the exact protected representation layer — bytes, canonical form, or graph semantics — together with payload-type binding and transform-validity rules, so canonicalization-boundary and representation-drift semantics should not be left implicit.

- `RS-GR-381`, `RS-GR-382`, `RS-GR-383`, `RS-GR-384`, `RS-GR-385`, and `RS-GR-386` suggest that long-horizon provenance also depends on preserving the interpretation contract for verified statements — media type, predicate vocabulary, schema dialect, specVersion, and any required context bundle — so semantic-survival and schema-pinning semantics should not be left implicit.
- `RS-GR-387`, `RS-GR-388`, `RS-GR-389`, `RS-GR-390`, `RS-GR-391`, `RS-GR-392`, and `RS-GR-393` suggest that long-horizon provenance also depends on preserving why one issuer, functionary, or workload had standing to speak for a subject — delegation chain, namespace custody, step / predicate scope, workload registration state, and audience restrictions — so authority-scope and designated-speaker semantics should not be left implicit.
- `RS-GR-394`, `RS-GR-395`, `RS-GR-396`, `RS-GR-397`, `RS-GR-398`, and `RS-GR-399` suggest that long-horizon provenance also depends on preserving how many independent actors had to concur, what counted as independent, and whether thresholds were satisfied by distinct compromise domains rather than duplicated assent, so quorum-semantics and signer-independence semantics should not be left implicit.
- `RS-GR-400`, `RS-GR-401`, `RS-GR-402`, `RS-GR-403`, `RS-GR-404`, `RS-GR-405`, and `RS-GR-406` suggest that long-horizon provenance also depends on preserving how overlapping authorities, statements, or policies were resolved — delegation order, terminating or veto rules, agreement requirements, issuer-inclusion filters, AND-vs-OR composition, and no-match fallback — so conflict-resolution and precedence-profile semantics should not be left implicit.
- `RS-GR-407`, `RS-GR-408`, `RS-GR-409`, `RS-GR-410`, `RS-GR-411`, `RS-GR-412`, and `RS-GR-413` suggest that long-horizon provenance also depends on preserving why a verdict happened in practice — determining policies, explanation traces, default / skip-on-error path, attached obligations or advice, decision correlation ids, and verifier-build / bundle provenance — so decision-trace and replay-diagnostic semantics should not be left implicit.
- `RS-GR-414`, `RS-GR-415`, `RS-GR-416`, `RS-GR-417`, `RS-GR-418`, `RS-GR-419`, and `RS-GR-420` suggest that long-horizon provenance also depends on preserving the exact baseline corpus used for appraisal — reference values, endorsements, trust roots, policy-data bundles, and input-selection scope — so appraisal-input continuity should not be left implicit.
- `RS-GR-421`, `RS-GR-422`, `RS-GR-423`, `RS-GR-424`, `RS-GR-425`, `RS-GR-426`, and `RS-GR-427` suggest that long-horizon provenance also depends on preserving how evidence was actually acquired — collection topology, freshness-handle origin and verifier binding, claim-selection scope, relay / broker trust, and concrete observation fields or staged capture boundaries — so evidence-acquisition and observation-scope semantics should not be left implicit.
- `RS-GR-428`, `RS-GR-429`, `RS-GR-430`, `RS-GR-431`, `RS-GR-432`, and `RS-GR-433` suggest that long-horizon provenance also depends on preserving what a verifier was allowed to learn and keep — disclosure profile, mandatory versus optional reveal rules, issuer-defined disclosure bounds, omission semantics for absent fields, holder-binding for disclosed subsets, and retention intent — so disclosure-profile and omission semantics should not be left implicit.
- `RS-GR-434`, `RS-GR-435`, `RS-GR-436`, `RS-GR-437`, `RS-GR-438`, `RS-GR-439`, and `RS-GR-440` suggest that long-horizon provenance also depends on preserving the original verifier ask and how satisfaction was established — query language/version, preferred versus fallback alternatives, submission-requirement logic, mapping from returned objects back to request elements, and any policy boundary constraining what the verifier was allowed to ask — so request-contract and satisfaction-mapping semantics should not be left implicit.


## Design heuristics

- Separate retaliation, forgiveness, and exit into distinct policy dials.
- Treat apology/repair as attack surfaces, not just prosocial signals.
- Publish rehabilitation / re-entry semantics whenever a world sanctions, excludes, or ostracizes.
- If repair signals exist, separate their effect from the bare action policy with a no-signal comparison and a follow-through metric.
- In hybrid worlds, publish whether humans and artificial agents are judged by the same norm, and whether judgments are action-only or intention-aware.
- Publish reputation scope explicitly in hybrid worlds: individual-agent only, model family, provider, or all-AI spillover.
- Publish whether reputations attach to individuals, groups, or both, and whether stereotype fallback is allowed when individual evidence is sparse or costly.
- Publish whether intergroup competition exists and whether agents may observe, reward, punish, or rematch across group boundaries.
- Publish whether reputation is primarily private, partially synchronized, publicly shared, or centrally assigned, and how opinions move between those states.
- In any centralized-score lane, publish whether direct interaction can override the score and how quickly fresh behavior can repair it.
- Publish monitoring cadence / cost and evidence-transfer friction in trust or reputation lanes so reduced checking cost is not mistaken for moral improvement.
- Publish identity persistence, reset rights, newcomer priors, and history carryover semantics in any reputation, sanction, or leave/rematch lane.
- Publish actor identifiability separately from action visibility, including what identity cues exist and when they are revealed.
- Publish willingness-versus-ability semantics and recipient need / burden metadata in helping or partner-choice lanes.
- Publish whether inequality comes from luck, merit, endowment, productivity, need, or aligned combinations before comparing cooperation across unequal worlds.
- Publish scarce-allocation rule and allocator authority explicitly whenever multiple claimants compete for limited goods.
- Publish sanction metanorms explicitly: which responses are legitimate after a violation, whether observers are expected to act, and whether non-enforcement or anti-social punishment is itself sanctionable.
- Publish enforcer incentives, retaliation exposure, and higher-order oversight rights explicitly whenever a third party or institution punishes others.
- Publish whether preplay commitments or pledges exist, who can make them, and whether later action scoring is conditional on commitment state.
- Publish post-hoc signal cost, timing, and follow-through semantics whenever agents can talk about themselves after acting.
- Publish concurrent-relationship portfolio width, partner topology (same-partner versus different-partner), and lane salience whenever agents juggle more than one active obligation.
- Publish whether a world is framed as producing benefits or preventing harms, and whether payoffs are gains, losses, or mixed-sign.
- Publish when collective harm becomes visible, whether thresholds are fixed or uncertain, and how effort aggregates at the threshold.
- Publish whether a problem admits public solutions, private solutions, or both, and who can access each route.
- Publish loner externality and group-formation flexibility whenever an outside option or self-reliance route exists.
- Publish whether concurrent lanes are isolated, strategically linkable, or crosstalk-prone before treating retaliation, forgiveness, or repair as lane-local properties.
- Publish encounter topology, degree heterogeneity / clustering / assortativity, and whether cooperators or defectors can occupy hubs or bridges by design.
- Publish tie-formation, tie-dissolution, homophily, and prior-acquaintance rules whenever agents can choose or inherit relationships.
- Publish whether rules are exogenously imposed, endogenously chosen, or only nominally voted on whenever agents can shape their own institution.
- Publish electorate, vote threshold, and binding scope explicitly whenever only some agents choose a rule or only some agents are governed by it.
- Publish future-duty framing and support-visibility semantics explicitly whenever a world asks agents or institutions to act on behalf of future beneficiaries.
- Publish whether a legacy intervention targets impact, reputation, or both, whether action is publicly visible, and whether the measured effect survives delay.
- Publish whether future beneficiaries are only named, role-played through future design, advisory-represented, or backed by stronger scrutiny / accountability machinery in the present decision process.
- Publish whether a future-facing world supplies a desirable future, a believable path to reach it, explicit collective efficacy, or emotional benefits of acting together.
- Publish whether future-facing urgency is paired with meaning-focused coping, efficacy-based hope, and real action channels, or whether distress is simply induced and left unmanaged.
- Publish whether future-facing action is measured against matched-cost present-day helping, mixed-beneficiary helping, or willingness to accept near-term losses.
- Publish which fairness reference groups are explicit in a world and at what scale burdens are experienced before calling the institution fair.
- Publish whether future beneficiaries are anonymous future people, descendants, or caregiver-linked successors before calling a lane future-regarding in a universal sense.
- Publish voice symmetry, dialogue leadership, and direction of influence whenever generations interact, teach, or deliberate across age lines.
- Publish who is allowed to speak for future beneficiaries, how they are selected or authorized, and what cohort-balance / diversity constraints apply before calling a lane meaningfully future-representative.
- Publish whether a future-facing institution is one-off, periodic, permanent, or sunsetted; what anchor preserves memory; and how outputs must travel, be answered, or be reviewed across policy-cycle stages and leadership changes.
- Publish whether a future-facing intervention is one-shot, piloted, temporary-experimental, staged, or reversible after launch, along with declared scale-up, rollback, and phase-out criteria.
- Publish whether temporary measures really expire, what evidence is required for extension or retirement, and how much implementation load they add to the standing policy stock.
- Publish whether future beneficiaries are merely considered, treated as rights-holders, or equipped with proxy standing and remedy routes, and whether enforcement is declaratory, oversight-based, or implementation-forcing.
- Publish uncertainty default, science standard, harm threshold, and burden-of-proof semantics explicitly whenever future-facing harms are serious, cumulative, or potentially irreversible.
- Publish what event counts as provisional closure, conditional closure, and final release, plus whether post-closure monitoring is absent, fixed-term, trigger-extended, or effectively perpetual.
- Publish who still owns residual liability after nominal closure, how that can transfer, and what orphan / insolvency backstop applies if the sponsor fails or disappears.
- Publish exactly which verification bytes future stewards must retain locally and which dependencies must still be reachable before calling a provenance lane successor-safe.
- Keep role-reversal / universalisation baselines in the benchmark set so that “Golden Rule” remains testable rather than rhetorical.
- Prefer tiny, repeatable worlds with rich instrumentation over large worlds with poor diagnostics.

## Failure modes to watch

- A strategy that looks good only because the score ignores payoff asymmetry.
- A repair mechanism that can be cheaply faked by an adversary.
- A partner-choice world that accidentally rewards churn, search luck, or merely visible helpfulness instead of cooperative stability and real partner-maintenance.
- A reputation lane that hides whether agents are missing observations, drifting into `Unknown` reputations, or moving through a richer graded state space.
- A gossip-enabled lane that treats copied judgments as harmless plumbing instead of as a policy dial.
- A sanction world whose headline is really driven by an easy public apology or automatic re-entry path that the benchmark forgot to publish.
- A sanction world whose record expiry or countdown to rehabilitation is legible enough to invite end-of-sentence opportunism.
- A repair-signal lane that looks robust only because it grants extra error-correction bandwidth with no no-signal comparison.
- A disclosed-action / sequential lane that is compared against simultaneous play without publishing move-order and visibility rights.
- A universalisation baseline that is so underspecified it becomes non-falsifiable.
- A hybrid lane that quietly judges humans and artificial agents by different standards without saying so.
- A hybrid reputation lane where one bad AI poisons trust in all AIs but the benchmark pretends reputation is purely individual.
- A group-structured lane where stereotype compression or collective scoring is doing the work while the benchmark claims to measure individual trustworthiness.
- A “universalistic” lane that only looks broad-minded because intergroup competition is absent or because cross-boundary enforcement is quietly available to a mobile minority.
- A governance lane that looks better only because agents endorsed the rule, not because the rule itself is stronger.
- An institution-choice lane that quietly lets only a subset vote or bind itself while the headline claims describe whole-group governance.
- A reputation lane that looks robust only because consensus is hard-coded or because private disagreement was silently synchronized away.
- A centralized-score lane that is presented as generic reputation even though a sticky scalar score is doing the institutional work.
- A trust lane that looks better only because agents can cheaply stop monitoring or because evidence-sharing was made artificially expensive or easy.
- A reputation lane where cheap re-entry lets bad actors come back as 'new' while the benchmark quietly normalizes distrust of newcomers.
- A transparency lane where names, faces, or group labels change behavior even though action evidence was held fixed or hidden.
- A helping lane that quietly treats inability, overload, and deliberate refusal as the same negative act, or that penalizes need itself as a reputational flaw.
- A cooperation lane that looks harsher or softer only because inequality was framed as earned merit, or because resources and productivity were aligned in a way that changes fairness norms.
- A scarcity lane where a planner, allocator, or queue discipline is doing the institutional work while the benchmark claims the reciprocal agents solved fairness themselves.
- A sanction lane where punishment looks stable only because observers were socially trained to copy one enforcement style or because failing to punish was itself silently sanctionable.
- A sanction lane where cooperation rises only because punishers were paid, protected from retaliation, or heavily audited, while the benchmark reports the gain as if targets simply became more moral.
- A communication lane where commitments quietly create obligations or scoring changes, but the benchmark reports the gain as if plain reciprocity improved.
- A repair / speech lane where cheap self-signals launder ambiguous or selfish behavior into a good reputation because no signal-cost or no-signal baseline was published.
- A risk lane that looks more cooperative only because shocks became shared, correlated, or easier to smooth, while the benchmark reports the gain as if reciprocity itself improved.
- A solidarity lane where formal insurance or public fallback silently changes deservingness judgments, so observed helping is really a response to safety-net design rather than to the Golden Rule.
- A direct-reciprocity lane that only looks robust because agents have one focal relationship at a time while real obligations are concurrent and competing.
- A concurrent lane where borrowed leverage or accidental crosstalk is doing the institutional work while the benchmark reports the gain as if local reciprocity itself improved.
- A network lane that looks cooperative only because cooperators occupy hubs or bridge positions, or because clustered topology walls off defectors.
- A dynamic-network lane where homophily, segregation, or selective repulsion is doing the institutional work while the benchmark reports the gain as if reciprocity itself improved.
- A cooperation lane that looks more generous or harsher only because the same incentives were reframed from helping to harm prevention, or from gains to losses.
- A collective-risk lane where delayed damage, uncertain thresholds, or weakest-link brittleness are doing the institutional work while the benchmark reports the gain or collapse as if reciprocity itself changed.
- A triadic or small-group lane that looks more reciprocal only because a third player's bridge position selectively stabilizes one relationship and destabilizes another.
- A communication or leadership lane that looks more cooperative only because some members got coordination, coalition, or representative rights that others did not.
- A collective-action lane that looks less cooperative only because private protection or self-reliance became cheaply available.
- An outside-option lane that looks more cooperative only because loners impose little externality and groups reform flexibly after exit.
- A helping lane that looks colder only because needy agents had to ask under stigma or rejection risk while need stayed hidden by default.
- A mutual-aid lane that looks more caring only because requests were public or socially rewarded, not because action policy improved.
- An intergenerational lane that looks more sustainable only because the present cohort could lock successors into preservation, while the benchmark reports the gain as if reciprocity itself improved.
- A future-facing lane that looks more universal or caring only because absent beneficiaries were given a proxy or because future beneficiaries were framed as ingroup rather than outgroup.
- A future-facing lane that looks more farsighted only because the benchmark quietly moved benefits from remote generations to the next cohort while preserving the same “future generations” label.
- A future-facing lane that looks more cooperative only because future harms were made psychologically near, vivid, or intertemporally linked, not because the action policy itself became more Golden-Rule-like.
- A future-facing lane that looks more feasible or bipartisan only because the benchmark used a responsibility-to-future-generations frame or corrected hidden support norms for future-facing institutions.
- A future-facing lane that looks more principled only because a visible reputation legacy was activated or because the benchmark measured only the immediate post-prompt bump.
- A future-facing lane that looks more mobilizing only because the world made a positive future seem achievable, emotionally rewarding, or collectively efficacious.
- A future-facing lane that looks more engaged or more demoralized only because distress was paired with high-agency coping scaffolds or left to accumulate without them.
- A future-facing lane that looks more caring only because the world replaced anonymous future beneficiaries with one's own children or grandchildren while preserving the same “future generations” label.
- An intergenerational lane that looks more cooperative only because the world added youth-led or reciprocal dialogue, repeated contact, or ageism-reducing program structure, while the benchmark reports the gain as if the reciprocity policy itself improved.
- A future-facing lane that looks more farsighted only because future beneficiaries were given role-played or advisory voice, or because policymakers were placed under stronger long-horizon scrutiny, while the benchmark reports the gain as if the action norm itself improved.
- A sustainability lane that looks cleaner only because burdens were exported to other sectors, regions, or later cohorts, or because successors quietly inherited indefinite monitoring and upkeep work.
- A future-facing lane that looks more patient only because benefits were moved from mainly posthumous payoffs to within-lifetime or edge-of-lifetime payoffs, while the benchmark preserved the same abstract future-beneficiary label.
- A stewardship or resilience lane that looks more protective only because the world introduced hard harm floors, explicit tipping-point triggers, or mandatory review / switch rights, while the benchmark reports the gain as if the reciprocity policy itself improved.
- A future-facing lane that looks more representative only because the proxy changed from incumbents to youth, affected communities, experts, or a sortition sample while the benchmark preserved the same generic 'future generations are represented' headline.
- A future-facing institution that looks more durable only because it became permanent, anchored, and equipped with mandatory response pathways or memory transfer across political cycles, while the benchmark reports the gain as if current actors simply cared more about posterity.
- A future-facing lane that looks more protective only because future beneficiaries gained standing, representative access, lowered proof barriers, or stronger remedies, while the benchmark reports the gain as if the underlying reciprocity policy itself improved.
- A long-horizon risk lane that looks more careful only because the world switched from wait-for-proof to precaution, or shifted the burden of demonstrating safety onto present risk-creators, while the benchmark reports the gain as if agents simply cared more about the future.
- A stewardship lane that looks more successor-friendly only because assurance release was delayed, periodic review was added, or nominal closure was converted into conditional closure with ongoing controls.
- A liability lane that looks more protective only because orphan risk was pushed onto parents, pooled vehicles, or the state, while the benchmark reports the gain as if the underlying reciprocity norm improved.
- A successor-trust lane that looks more durable only because trust anchors can rotate, delegations are thresholded and revocable, or compromise has an out-of-band recovery path, while the benchmark reports the gain as if reciprocity itself improved.
- A successor-provenance lane that looks more durable only because statements are registered in append-only transparency services, inclusion and history proofs are verified, or multiple independent services and monitors are trusted, while the benchmark reports the gain as if reciprocity itself improved.
- A successor-provenance lane that looks more durable only because verification kept working while the original services were still reachable, but the archive failed to retain the compact receipt / bundle, trust roots, or re-anchoring path needed for later offline verification.

## Minimal next tranche

- Scorecard: anti-vampire metrics.
- World: leave/rematch.
- Measurement split: observable help versus hidden partner-maintenance help.
- Reputation contract: one minimal public/private assessment-update lane.
- Reputation granularity check: publish binary versus graded/ternary reputation alphabet and transition semantics.
- Information split inside that lane: sparse observation versus fading / `Unknown` reputations.
- Gossip contract: explicit cadence / fan-in / trust-weight metadata plus one no-gossip comparison.
- Rehabilitation timing check: bounded-memory exclusion lane with declared record-retention and countdown legibility semantics.
- Rehabilitation contract: explicit exclusion duration / re-entry / apology visibility metadata in any sanction lane.
- Repair-signal check: one no-signal companion comparison plus one follow-through or abuse metric.
- Baseline recheck: rerun TFT / WSLS / Grim in one noisy voluntary-repetition slice once leave/rematch exists.
- Strategy family: longer-memory reactive baseline.
- Institution slice: one disclosed-action / leader-follower companion lane kept separate from simultaneous-play claims.
- Claim policy: forbid payoff-only claims in extortion settings.
- Hybrid assessment check: one human-only versus hybrid comparison with declared agent-type judgment symmetry.
- Hybrid spillover check: one no-class-spillover baseline with declared reputation scope.
- Collective-reputation check: one individual-only baseline compared against one collective or stereotype-enabled assessment lane.
- Intergroup-universalism check: one no-cross-boundary-enforcement baseline compared against one selective-mobility enforcement lane.
- Reputation-governance check: one mostly-private-opinion baseline compared against one synchronized-public lane with declared source weighting.
- Centralized-score check: one revisable local-reputation baseline compared against one scalar social-credit-style score lane with declared override / repair semantics.
- Monitoring-economics check: one low-friction baseline compared against one costly-observation / costly-evidence-transfer lane with declared trust metric semantics.
- Helping-evaluation check: one lane with separate willingness-versus-ability and recipient need / burden metadata compared against one collapsed-evaluation baseline.
- Identity-persistence check: one stable-history baseline compared against one cheap-reset / whitewashing-permitted lane with declared newcomer priors.
- Disclosure-contract check: one anonymous visible-action baseline compared against one identifiable private-action lane and one identifiable public-history lane.
- Shock-structure check: one deterministic or idiosyncratic-risk baseline compared against one shared-shock / common-fate lane with declared pooling and payout-timing semantics.
- Fallback-institution check: one no-formal-protection baseline compared against one insurance / public-fallback lane with declared eligibility, crowd-out, and unused-protection semantics.
- Concurrent-portfolio check: one single-channel baseline compared against same-partner and different-partner concurrent worlds with declared lane salience.
- Cross-lane-linkage check: one channel-isolated baseline compared against one intentionally linked or crosstalk-prone concurrent world with declared spillover semantics.
- Encounter-topology check: one well-mixed or degree-neutral baseline compared against one clustered / hub-skewed / degree-assorted network with declared bridge metrics.
- Tie-formation check: one forced-mixing or no-homophily baseline compared against one homophily-enabled or selective-separation rewiring lane with declared prior-acquaintance and tie-dissolution semantics.
- Inequality-source check: one luck-framed unequal world compared against one merit-framed or productivity-skewed unequal world with declared capability alignment.
- Scarcity-allocation check: one automatic-division baseline compared against one planner or third-party-allocation lane with declared equality / need / merit semantics.
- Sanction-metanorm check: one lane with declared observer response rights and duties compared against one lane where non-enforcement is neutral.
- Enforcer-governance check: one nonprofitable, retaliation-exposed sanctioner baseline compared against one higher-order-monitored or paid-sanctioner lane.
- Commitment-stage check: one no-pledge baseline compared against one explicit pledge / vow / joint-commitment lane with declared breach-scoring semantics.
- Self-signal check: one no-signal or costly-signal baseline compared against one cheap post-hoc self-signaling lane with declared follow-through rule.
- Harm-accounting check: one help/provision baseline compared against one harm/prevention framing with declared gain/loss sign structure.
- Collective-damage check: one immediate-harm and certain-threshold baseline compared against one delayed-harm or weakest-link / uncertain-threshold lane.
- Triadic-structure check: one dyadic baseline compared against one explicitly linked triadic or other small-group lane with declared third-player position and information-scope semantics.
- Delegated-coordination check: one no-delegation baseline compared against one partial-voice, coalition-stage, or representative-selection lane with declared speech rights and leader / representative selection rules.
- Private-solution check: one no-private-option baseline compared against one mixed public/private-solution lane with declared access asymmetry and relative efficacy.
- Outside-option-semantics check: one fixed-group or no-outside-option baseline compared against one flexible-group or low-loner-externality outside-option lane.
- Need-revelation check: one visible-need or unsolicited-offer baseline compared against one private-need / explicit-ask lane with declared refusal semantics.
- Request-visibility check: one private-request baseline compared against one public or recognized-request lane with declared audience and subgroup-asymmetry semantics.
- Successor-binding check: one fully revisable intergenerational baseline compared against one time-limited or escape-enabled successor-binding lane with declared lock duration and override semantics.
- Future-beneficiary-representation check: one no-proxy and universal-beneficiary baseline compared against one guardian / future-design / socially narrowed future-beneficiary lane with declared representation powers and beneficiary scope.
- Future-generation-depth check: one near-horizon baseline compared against one farther-horizon future-beneficiary lane with declared cohort-distance semantics.
- Future-vividness check: one low-link / low-vividness baseline compared against one intertemporally linked or psychologically proximal future-beneficiary lane with declared agency semantics.
- Closure-release check: one immediate-release baseline compared against one conditional-closure or delayed-release lane with declared monitoring-window and protectiveness-review semantics.
- Residual-liability check: one operator-retains-liability baseline compared against one transfer / pooled-backstop lane with declared insolvency and orphan-risk semantics.
- Future-duty-frame check: one neutral or alternate-frame baseline compared against one explicit responsibility-to-future-generations lane with declared norm-language semantics.
- Future-support-visibility check: one hidden-support baseline compared against one norm-corrected or support-salience lane with declared coalition-feasibility cues.
- Legacy-type-and-durability check: one no-legacy baseline compared against one impact-legacy or reputation-legacy lane with declared action visibility and delayed follow-up.
- Positive-future-and-efficacy check: one neutral baseline compared against one positive-future or efficacy-rich lane with declared desirability / achievability / emotional-benefit semantics.
- Distress-channeling check: one low-scaffold future-burden baseline compared against one meaning-focused or agency-supported variant with declared action channels and follow-up behavior / distress semantics.
- Present-versus-future costly-help check: one matched-cost present-beneficiary baseline compared against one future-beneficiary and one mixed-beneficiary lane with declared sacrifice semantics.
- Fairness-reference-group check: one same-payoff baseline compared against household/local, vulnerable-subgroup, societal, and future-generation fairness variants with declared burden scale.
- Descendant-specific-beneficiary check: one matched-cost abstract-future baseline compared against child/grandchild or caregiver-activated beneficiary variants with declared kinship scope and household-burden semantics.
- Intergenerational-dialogue check: one one-way-instruction baseline compared against youth-led and reciprocal-contact variants with declared voice symmetry, influence direction, and contact cadence.
- Future-voice-insertion check: one no-voice baseline compared against future-design, soft-advice, and stronger scrutiny / accountability variants with declared powers.
- Problem-shifting / rolling-stewardship check: one low-maintenance baseline compared against open-ended successor-stewardship or burden-exporting variants with declared sectoral / geographical / temporal shift semantics.
- Lifespan-boundary check: one matched-benefit within-lifetime baseline compared against one edge-of-lifetime and one mainly posthumous-payoff world with declared descendant / caregiver time-horizon cues.
- Threshold-and-trigger check: one smooth-tradeoff baseline compared against one significant-harm-floor and one trigger-driven pathway world with declared indicators, review rights, and switch authority.
- Representative-source-and-selection check: one incumbent or expert-appointed baseline compared against youth, affected-community, and randomly selected proxy-voice worlds under matched formal powers with declared contestability semantics.
- Permanence-and-anchor check: one one-off consultation baseline compared against periodic, permanent, and sunsetted future-facing institutions with declared anchor agency, knowledge-transfer, and mandatory-response semantics.

- Future-impact-accounting check: one generic-future-language baseline compared against one explicit future-check / trade-off-accounting / written-response lane with declared review cadence.
- Discount-schedule check: one matched-behavior baseline compared against one lower-rate / declining-rate or alternate-valuation lane with declared demographic and future-bias assumptions.
- Future-rights-and-remedy check: one symbolic-recognition or declaration-only baseline compared against one broad-standing / implementation-forcing world with declared representative route and remedy class semantics.
- Precaution-and-proof-burden check: one wait-for-proof baseline compared against one precautionary or shifted-proof-burden world with declared science threshold and irreversible-harm trigger semantics.
- Avoidance-and-substitutability check: one compensate-later or weak-avoidance baseline compared against one avoidance-first or non-substitutable-loss world with declared reversibility timescale and restoration order semantics.
- Robustness-and-regret-architecture check: one reference-scenario-optimal baseline compared against one robust / no-regret or adaptive-pathway world with declared stress-tested uncertainties, vulnerabilities, and option-preservation devices.
- Pilotability-and-reversibility check: one one-shot permanent baseline compared against one piloted, temporary-experimental, or reversible-trial world with declared scale-up / rollback and learning semantics.
- Sunset-and-policy-stock-load check: one persist-until-repeal baseline compared against one auto-expiring, affirmative-reauthorization, or stock-retirement-disciplined world with declared extension evidence and implementation-load semantics.


## New local constraint from this archive

The new memory-one tradeoff snapshot tightens the problem statement:
- in a 200k analytic random sample of memory-one strategies,
- no candidate simultaneously achieved nonnegative fairness versus extortion, high self-play (`>= 2.5`), and low exploitation of Always-Cooperate (`<= 0.1` gain).

Treat this as a tranche-selection clue. Before spending effort on broader memory-one search, test whether modestly richer spaces (longer memory or exit) break this tension.

- Prefunding-and-assurance check: one same-behavior unfunded or pay-as-you-go baseline compared against one bonded, insured, or ring-fenced-prefunded world with declared reserve governance, confidence level, and shortfall bearer semantics.
- Deferred-maintenance-and-asset-ledger check: one opaque asset-condition baseline compared against one inventory-rich, lifecycle-costed, backlog-published world with declared depreciation / ASI / funding-adequacy semantics.
- Successor-competence check: one record-rich baseline compared against one competency-rich succession-planned world with declared staffing depth, overlap, training, and geographic distribution.
- Rehearsed-role check: one documented-playbook baseline compared against one drilled / exercised world with declared role validation, interface rehearsal, and after-action correction cadence.

- Interoperability-and-vendor-exit check: one bespoke / captive-format baseline compared against one open-standard, API-exportable, persistent-identifier-rich lane with declared semantic-loss and re-homing semantics.
- Manual-fallback-and-graceful-degradation check: one hard-outage or automation-dependent baseline compared against one degraded-service / manual-processing / alternate-facility lane with declared essential-record, communications, and staffing survivability semantics.

- Fixity-refresh-and-format-migration check: one ingest-only / passive-retention baseline compared against one recurring-fixity-audit, repair-capable, preservation-action-planned world with declared audit cadence, repair authority, and unsustainable-format migration semantics.
- Crypto-agility-and-algorithm-transition check: one static-crypto baseline compared against one migration-ready world with declared inventory / planning, algorithm-transition, validation / monitoring, and future-migration semantics.
- Trust-anchor-rotation-and-delegated-authority check: one static-root / manual-emergency baseline compared against one rotation-ready, thresholded, delegable world with declared cryptoperiod, propagation window, revocation, and out-of-band recovery semantics.
- Transparency-log-and-monitor-plurality check: one signed-but-unlogged or single-service / unmonitored baseline compared against one append-only, proof-verifiable, monitored, or multi-service world with declared inclusion, consistency, receipt-discovery, and selective-submission semantics.
- Witnessed-checkpoint-and-split-view-resistance check: one append-only-but-unwitnessed or low-self-audit baseline compared against one witness-quorum, client-cross-checking, or gossip-backed world with declared checkpoint, quorum, configuration, and equivocation-response semantics.
- Temporal-validity-and-secure-time check: one timeless / unauthenticated-clock baseline compared against one expiry-bounded, securely-attested, or renewable-evidence world with declared freshness window, time-source bootstrap, publication-latency, and stale-proof response semantics.
- Portable-evidence-packet-and-offline-verification check: one live-service-dependent baseline compared against one self-contained bundle / receipt world with declared retained bytes, offline-verification scope, cross-client readability, trust-root survival, and successor-service re-anchoring semantics.
- Verifier-policy-snapshot-and-deterministic-appraisal check: one evidence-rich but policy-implicit baseline compared against one profile-identified, policy-versioned world with declared trust roots, identity / issuer constraints, claim-check strictness, historical-policy replay, and historical-vs-current-policy disagreement semantics.
- Status-semantics-and-supersession-history check: one proof-rich but status-implicit baseline compared against one world with declared revocation / suspension / unknown / expiry / end-of-life / redirection semantics, status-freshness source, negative-evidence retention, compromise-time handling, and historical-validity-versus-current-acceptability distinction.
- Subject-binding-and-resolver-independence check: one signed-name / mutable-alias baseline compared against one digest- or intrinsic-ID-centered world with declared core subject identifier, alias history, multi-variant resolution semantics, attachment / status correlation key, and signed alias-to-subject binding rules.
- Canonicalization-and-transform-semantics check: one verified-bytes baseline compared against one world with declared protected representation layer, canonicalization profile, payload type, and transform-validity semantics.
- Semantic-survival-and-schema-pinning check: one bytes-verifiable-but-semantic-live-lookup baseline compared against one locally pinned media-type / predicate-type / schema / context bundle with declared unknown-extension handling and version-mismatch semantics.
- Authority-scope-and-designated-speaker check: one signed-and-known-issuer baseline compared against one world with declared issuer standing, delegated role or registration entry, namespace / path custody, purpose / predicate / step scope, workload / selector or parent constraints, and any audience or relying-party restrictions.
- Quorum-semantics-and-signer-independence check: one threshold-free or any-one-authority baseline compared against one world with declared threshold / quorum rule, unit of distinctness, separation-of-duty assumptions, witness or transparency-service diversity requirements, and quorum-failure semantics.
- Conflict-resolution-and-precedence-profile check: one any-valid-claim / implicit-priority baseline compared against one world with declared delegation order, terminating or veto semantics, same-facts agreement requirement, issuer-inclusion filter, AND-vs-OR composition, and no-match / abstention handling.
- Decision-trace-and-replay-diagnostic check: one final-verdict-only baseline compared against one world with declared decision / request ids, determining policies or rules, default / skip-on-error route, retained obligations / advice, and verifier build / bundle provenance.
- Reference-baseline-and-appraisal-input-continuity check: one verdict-rich but baseline-implicit world compared against one world with declared reference-value corpus, endorsement set, trust-root source, policy-data bundle snapshot, input-selection scope, and missing- or stale-baseline fallback semantics.
- Evidence-acquisition-and-observation-scope check: one evidence-retaining but acquisition-implicit world compared against one world with declared collection topology, freshness-handle origin and binding, claim-selection and event-log scope, intermediary trust assumptions, captured observation fields, staged capture boundary, and stale- or partial-evidence fallback semantics.
- Disclosure-profile-and-omission-semantics check: one selectively presented but disclosure-implicit world compared against one world with declared disclosure profile, mandatory versus optional claims, issuer-defined disclosure bounds, absent-field semantics, holder-binding requirements, unlinkability posture, and verifier retention-intent / discard expectations.
- `RS-GR-441`, `RS-GR-442`, `RS-GR-443`, `RS-GR-444`, `RS-GR-445`, `RS-GR-446`, and `RS-GR-447` suggest that long-horizon provenance also depends on preserving why a proof was valid for this verifier, origin, route, and session — `client_id` / audience targeting, nonce or wallet-nonce freshness, session-transcript / handover contents, response-channel or endpoint binding, proof-option domain / challenge semantics, key-binding requirements, and replay-window policy — so verifier-targeting and replay-scope semantics should not be left implicit.
- `RS-GR-448`, `RS-GR-449`, `RS-GR-450`, `RS-GR-451`, `RS-GR-452`, `RS-GR-453`, `RS-GR-454`, and `RS-GR-455` suggest that long-horizon provenance also depends on preserving how participant metadata was resolved and trusted — discovery or identifier-prefix mode, trust-chain or signed-metadata evidence, policy-applied endpoint / key / algorithm surfaces, DID-resolution outputs, validation outcomes, and cache/version state — so metadata-resolution and capability-continuity semantics should not be left implicit.
- `RS-GR-456`, `RS-GR-457`, `RS-GR-458`, `RS-GR-459`, `RS-GR-460`, `RS-GR-461`, `RS-GR-462`, and `RS-GR-463` suggest that long-horizon provenance also depends on preserving not just the supported capability sets but the exact negotiated profile — chosen format, proof type, response mode, cryptographic algorithms, request / response protection posture, downgrade policy, and fail-closed behavior on unsupported asks — so capability-negotiation and downgrade-resistance semantics should not be left implicit.
- `RS-GR-464`, `RS-GR-465`, `RS-GR-466`, `RS-GR-467`, `RS-GR-468`, `RS-GR-469`, and `RS-GR-470` suggest that long-horizon provenance also depends on preserving what kind of authenticator or key container stood behind a proof — user-presence and user-verification signals, authentication intent, device-bound versus syncable posture, attestation or authenticator-class evidence, and whether holder binding was required or waived — so authenticator-assurance and device-binding semantics should not be left implicit.
- `RS-GR-471`, `RS-GR-472`, `RS-GR-473`, `RS-GR-474`, `RS-GR-475`, `RS-GR-476`, and `RS-GR-477` suggest that long-horizon provenance also depends on preserving what exact transaction or authorization the user approved — structured authorization details or transaction data, granted subset versus original ask, signed-request or pushed-request protection, proof linkage to the approved object, and the rule for deciding whether a later ask is materially the same — so transaction-intent and approval continuity should not be left implicit.
- Transaction-intent-and-approval check: one proof-producing world compared against one world with declared `authorization_details` / `transaction_data`, granted subset, request-object or pushed-request integrity path, proof linkage to the approved object, and explicit same-versus-different approval comparison rules.

- `RS-GR-478`, `RS-GR-479`, `RS-GR-480`, `RS-GR-481`, `RS-GR-482`, `RS-GR-483`, `RS-GR-484`, and `RS-GR-485` suggest that long-horizon provenance also depends on preserving correlation scope — whether presentations used globally stable identifiers, sector-pairwise pseudonyms, unlinkable derived proofs, privacy-preserving status checks, or leak-prone issuer / type metadata — so correlation-scope and linkability-boundary semantics should not be left implicit.
- Correlation-scope-and-linkability check: one globally linkable or stable-subject baseline compared against one verifier-pairwise or sector-pairwise world and one unlinkable-derived-proof / privacy-preserving-status world with declared status-check path, issuer / type leakage posture, and intended correlation boundary.
- `RS-GR-486`, `RS-GR-487`, `RS-GR-488`, `RS-GR-489`, `RS-GR-490`, `RS-GR-491`, and `RS-GR-492` suggest that long-horizon provenance also depends on preserving the delivery path itself — whether the request traveled through front-channel URLs or a protected `request_uri`, whether the response came back by redirect, body post, or encrypted JWT, which browser / frontend / backend / relay surfaces could see plaintext, and whether out-of-band response delivery had an explicit session-correlation closure — so delivery-path and intermediary-visibility semantics should not be left implicit.
- Delivery-path-and-intermediary-visibility check: one redirect- and URL-exposed baseline compared against one JAR/PAR and body-only world and one encrypted-response world with declared plaintext observers, response-code handback, and front-channel minimization semantics.

- `RS-GR-493`, `RS-GR-494`, `RS-GR-495`, `RS-GR-496`, `RS-GR-497`, `RS-GR-498`, `RS-GR-499`, and `RS-GR-500` suggest that long-horizon provenance also depends on preserving the approval rendering itself — what fields, labels, order, locale, and formatting the human actually saw; whether those labels came from issuer metadata or verifier / merchant input; whether the final ceremony ran in user-agent or wallet chrome versus attacker-frameable page content; and whether the rendered approval was checked against the authoritative backend object — so approval-rendering and trusted-display semantics should not be left implicit.
- Approval-rendering-and-trusted-display check: one merchant- or page-rendered baseline compared against one user-agent / wallet-controlled rendering world and one mismatch-checked world with declared locale, label source, field order, anti-redressing posture, and render-to-backend comparison semantics.

- `RS-GR-501`, `RS-GR-502`, `RS-GR-503`, `RS-GR-504`, `RS-GR-505`, `RS-GR-506`, `RS-GR-507`, and `RS-GR-508` suggest that long-horizon provenance also depends on preserving ceremony topology itself — whether the journey was same-device, cross-device, or hybrid; whether wallet invocation was untargeted QR/deep-link scanning or a targeted app launch; whether app dispatch used claimed HTTPS links or weaker custom schemes; and whether any explicit proximity or cross-channel participation evidence linked the responding device to the displayed request — so device-split and invocation-route semantics should not be left implicit.
- Ceremony-topology-and-device-split check: one same-device targeted-app baseline compared against one untargeted QR cross-device world and one hybrid / proximity-proven world with declared invocation route, app-identity assurance posture, and cross-channel participation semantics.
- Implementation move: ship one machine-checkable successor-safe ceremony receipt that records request contract, verifier targeting, delivery path, approval surface, ceremony topology, linkability posture, and retained-evidence references in one compact object, so future sessions can validate and diff the decisive ceremony facts without retaining bulky payloads.
- `RS-GR-509` and `RS-GR-510` suggest that once the archive has that compact receipt, the next size-control move is to content-address it via deterministic canonicalization plus a hash-named locator, so downstream notes can cite one stable digest / `ni` handle instead of re-copying the receipt body whenever the underlying ceremony contract has not changed.
- `RS-GR-514` and `RS-GR-515` suggest that once the archive can assess a receipt, it should also collapse that verdict into one explicit disposition carrying the residual-risk response and required follow-up actions, so warning/fail findings do not drift forward as ambiguous prose without custody of what the steward intended to do next.

- `RS-GR-516` and `RS-GR-517` suggest that once the archive has an explicit disposition for a weak receipt, the next custody move is one tiny remediation plan carrying the open finding codes, exact receipt paths to repair, closure tests, and promotion gate, so future stewards inherit not just a warning label but a compact route back to claim-ready citation.
- `RS-GR-518` and `RS-GR-519` suggest that once the archive has a current receipt package, the final custody move is one tiny authorization decision carrying the basis checks and terms for claim-ready citation, so future stewards inherit the explicit admission verdict rather than reconstructing it from assessment, remediation, and chat history.
- `RS-GR-520` and `RS-GR-521` suggest that once a once-weak package later becomes claim-ready, the archive should also keep one tiny promotion record carrying prior/current locators, prior/current assessment and authorization state, and the exact finding codes that closed or reopened, so future stewards inherit the closure basis rather than just the latest green verdict.
- `RS-GR-522` and `RS-GR-523` suggest that once a package is claim-ready, the archive should also keep one tiny review watch carrying the reviewed-on date, no-later-than review interval, reopen-trigger codes, and regeneration sequence, so future stewards inherit freshness custody rather than assuming one old green authorization stays current forever.
- `RS-GR-524` and `RS-GR-525` suggest that once a package is under watch, the archive should also keep one tiny review verdict for each actual review event carrying the as-of date, trigger matches, and explicit keep-citing versus reopen-now decision, so future stewards inherit the freshness judgment rather than only the freshness rule.
- `RS-GR-526` and `RS-GR-527` suggest that once a review verdict exists, the archive should also keep one tiny citation advisory carrying the downstream keep-versus-withdraw decision for existing and new citations, so future stewards inherit not just freshness judgment but the actual citation handling that followed from it.
- `RS-GR-528`, `RS-GR-529`, and `RS-GR-530` suggest that once the archive has a current successor-safe ceremony receipt package, it should also keep one tiny package manifest carrying the active locator, current package-state decisions, authoritative component roles and paths, and one file-level digest per component, so future stewards inherit not just the current verdict but the stable root membership and fixity of the package that earned it.
- `RS-GR-531`, `RS-GR-532`, and `RS-GR-533` suggest that once the archive has a compact current package manifest, it should also keep one tiny package supersession record whenever that manifest is refreshed or replaced, carrying prior/current manifest references, receipt-locator continuity, replaced component roles, and explicit replacement guidance, so future stewards inherit not just current package membership but the exact authoritative replacement path when package roots change.

- `RS-GR-534`, `RS-GR-535`, and `RS-GR-536` suggest that once the archive has more than one successor-safe ceremony receipt package supersession record, it should also keep one tiny package lineage record naming the authoritative head manifest, the ordered manifest and supersession chains, locator continuity across the line, and the current review/advisory basis that keeps that head authoritative, so future stewards inherit not just pairwise replacements but the current package root in one machine-checkable object.

- `RS-GR-537`, `RS-GR-538`, and `RS-GR-539` suggest that once the archive has package lineage, it should also keep one tiny package-head pointer using standard relation semantics to name the live authoritative manifest, the lineage that backs it, the current review/advisory status artifacts, and the immediate predecessor when one exists, so future stewards inherit not just the authority chain but the cheapest possible discovery path to the current package root.

- `RS-GR-540`, `RS-GR-541`, and `RS-GR-542` suggest that once the archive has a package head, it should also keep one tiny package-status-card object that the head exposes as its live `status` resource, collapsing the authoritative manifest, active locator digest, live review window, as-of review verdict, citation guidance, and current citable posture into one machine-checkable stewarding object so future inheritors do not need to open several neighboring status files just to answer whether the package head is safe to cite right now.
- `RS-GR-543`, `RS-GR-544`, and `RS-GR-545` suggest that once the archive still retains superseded package manifests for audit, it should also keep one tiny package-redirect object rooted at the superseded manifest that uses registered `cite-as`, `successor-version`, `latest-version`, `status`, and `describedby` semantics to point future inheritors at the preferred current package-reference target, successor manifest, and live status card, so they do not have to reconstruct replacement guidance from several neighboring files.


- `RS-GR-546`, `RS-GR-547`, and `RS-GR-548` suggest that once the archive has package heads for live successor-safe ceremony receipt roots and redirects for superseded ones, it should also keep one tiny package catalog listing the live head for each retained package family plus any retained superseded-package redirects, so future inheritors can discover the current package roots from one archive entry point instead of browsing lineage and redirect files family by family.

- The current successor-safe ceremony package surface now includes a compact package verification report beside the package head. Use it to answer what local checks actually ran here and where the Python-pass / Rust-blocked cloudtainer boundary currently sits, instead of inferring that from scattered command transcripts.

- `RS-GR-549`, `RS-GR-550`, `RS-GR-551`, and `RS-GR-552` suggest that once the archive exposes a live package verification report, it should also keep one tiny package-claim-scope artifact that says which downstream claims the current local verification basis supports and which remain out of scope, so future inheritors do not overstate a Python-pass / Rust-blocked package as if it were fully runtime-verified here.
