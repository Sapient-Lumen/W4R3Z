# Research Opinions and Build Priorities

This document states concrete opinions after the research pass and maps them to execution choices.

References: [docs/RESEARCH_SOURCES.md](RESEARCH_SOURCES.md), [docs/RESEARCH_AGENDA.md](RESEARCH_AGENDA.md).

## Strong Opinions

1. Concord should optimize for robustness evidence, not strategy leaderboards.
2. Rust should remain the only authority for simulation semantics and artifact hashing.
3. Formal methods should be additive and staged: SMT first, probabilistic model checking second.
4. Python should orchestrate workflows and reporting, but never redefine simulation mathematics.
5. Every scientific claim must declare evidence class: empirical estimate, formal proof, or temporary assumption.
6. Anti-extortion search should never optimize raw self-payoff alone; it must record payoff asymmetry and recovery behavior.
7. Strategy-space expansions should be phased and benchmarked against simpler spaces before being treated as progress.
8. Simultaneous-move, leave/rematch, and disclosed-action worlds should be treated as different institutions, not as cosmetic variants of one benchmark.
9. In partner-choice worlds, observable cooperation should not be treated as interchangeable with hidden partner-maintenance help.
10. Reputation lanes must declare assessment/update rules explicitly; "reputation on" is not a sufficient world description.
11. Sparse observation and fading / `Unknown` reputations should be treated as different institutions, not collapsed into one noisy-reputation lane.
12. Gossip cadence, fan-in, and trust weighting belong in the world contract; they are not background communication detail.
13. In sanction or exclusion worlds, rehabilitation and re-entry are part of institution design, not optional aftercare.
14. Repair-signal channels need explicit visibility, follow-through, and abuse semantics; otherwise communicative error correction can be mistaken for a policy breakthrough.
15. Reputation alphabet and update granularity belong in the world contract; binary and graded reputation lanes are different institutions.
16. If misconduct records expire, record-retention length and rehabilitation legibility must be published; visible countdowns can change enforcement incentives.
17. Hybrid human/AI reciprocity worlds are different institutions from human-only worlds; agent-type assessment asymmetries and consensus effects belong in the world contract.
18. Reputation scope belongs in the world contract for hybrid worlds; one failure may attach to an individual, a family, a provider, or all AIs.
19. Collective versus individual reputation is a world-contract choice; group-level assessment and stereotype fallback can change cooperation without any change in base action policy.
20. Universalistic cooperation across group boundaries is institution-sensitive; intergroup competition and cross-boundary mobility belong in the world contract.
21. Reputation governance topology belongs in the world contract; private opinions, synchronized public consensus, and centralized scores are different institutions.
22. Centralized scalar scores are not innocent reputation baselines; they can crowd out direct trust repair and harden stale bias.
23. Monitoring cadence and observation / evidence-transfer costs belong in the world contract; trust gains can come from reduced checking costs rather than from better action policy.
24. Helping evaluation should separate unwillingness, inability, overload, and recipient burden; otherwise the benchmark can reward harshness or victim-blame dynamics.
25. Inequality source and capability alignment belong in the world contract; merit-framed, luck-framed, endowment-skewed, and productivity-skewed worlds are different institutions.
26. Scarce-allocation rule and planner authority belong in the world contract; equality, need, merit, and reciprocity-conditioned allocation should not be collapsed into one redistribution afterthought.
27. Punishment metanorms belong in the world contract; whether observers ignore, gossip, exclude, confront, or materially punish violations is part of the institution, not local color.
28. Enforcer incentives, retaliation exposure, and higher-order oversight belong in the world contract; sanction outcomes can move because punishers are protected, audited, elected, or paid, not because targets became more reciprocal.
29. Commitment stages belong in the world contract; a world with pledges, vows, or public commitments is not just a talkative version of the same game, because commitment state can change obligations and third-party scoring.
30. Post-hoc self-signals belong in the world contract; cheap self-presentation should not be conflated with repair or sincerity unless signal cost, timing, and follow-through semantics are published.
31. Concurrent relationship portfolio width and partner topology belong in the world contract; a single repeated relationship, two same-partner lanes, and two different-partner lanes are different institutions.
32. Cross-lane linkage, spillover, and crosstalk belong in the world contract; borrowed leverage and accidental memory transfer can change reciprocity without any change in local action policy.
33. Encounter topology belongs in the world contract; hubs, bridges, clustering, and assortativity can sustain or block cooperation without any change in local action policy.
34. Tie formation, homophily, and rewiring rules belong in the world contract; stable cooperation can come from segregation or selective separation rather than from agents becoming more reciprocal.
35. Help-versus-harm framing and gain/loss sign structure belong in the world contract; the same incentives can move cooperation differently when cast as doing good versus avoiding harm, or as gains versus losses.
36. Collective harm latency and threshold semantics belong in the world contract; delayed damage, uncertain thresholds, and weakest-link aggregation can change cooperation without any change in base policy.
37. Private-solution availability belongs in the world contract; a world with public and private protection routes is not just a richer action set, because self-reliance can crowd out shared provision and amplify inequality.
38. Outside-option semantics belong in the world contract; the same opt-out right can help or hurt depending on loner externality and whether groups are fixed or form flexibly.
39. Need revelation and ask stages belong in the world contract; a world with private need and explicit asking is a different institution from one with visible need or unsolicited offers.
40. Request visibility, audience, and recognition belong in the world contract; public asking can reduce or increase social cost depending on who sees the request and who is socially licensed to ask.
41. Successor binding belongs in the world contract; a world where the present cohort can constrain the next cohort is not the same institution as one where each cohort can fully revise inherited policy.
42. Future-beneficiary representation and social scope belong in the world contract; proxy voice, guardian advice, universal future beneficiaries, and ingroup-framed descendants are different institutions.
43. Future-generation depth belongs in the world contract; helping the next cohort, the seventh generation, and remote future generations are different institutions rather than one story stretched across time.
44. Future vividness and intertemporal linkage belong in the world contract; direct cross-cohort links, psychological proximity, and future-self imagination can change behavior without changing the underlying reciprocity norm.
45. Future-responsibility framing and support visibility belong in the world contract; responsibility to future generations, responsibility for present harms, and revealed versus hidden support for future-facing institutions change uptake without changing the underlying reciprocity rule.
46. Legacy motive type and action visibility belong in the world contract; impact legacy, reputation legacy, public observability, and effect durability are different mechanisms rather than one generic future-care dial.
47. Positive future imagination, achievability, and emotional benefits belong in the world contract; desirable futures, collective efficacy, and positive affective payoff are different mechanisms rather than one generic hope intervention.
48. Distress channeling and coping scaffolds belong in the world contract; future-facing worry can suppress or mobilize action depending on meaning-focused coping, agency, and hope-from-action rather than on distress intensity alone.
49. Present-day solidarity versus future regard belongs in the world contract; future concern can coexist with immediate costly helping, but willingness still depends on who bears current sacrifice and whether present-day beneficiaries are made salient.
50. Burden-sharing scale and fairness reference group belong in the world contract; household fairness, local-community fairness, subgroup protection, broad societal justice, and fairness to future generations are different institutions rather than one justice scalar.
51. Descendant-specific beneficiary framing and kinship scope belong in the world contract; care for one's children or grandchildren, caregiver-role activation, and concern for anonymous future people are different institutions rather than one future-regard scalar.
52. Intergenerational dialogue and bidirectional influence belong in the world contract; one-way instruction, youth-led dialogue, reciprocal exchange, and stereotype-reducing sustained contact are different institutions rather than one communication knob.
53. Future-voice insertion and throughput accountability belong in the world contract; nominal recognition, future-design role play, soft advisory institutions, and stronger scrutiny / accountability bodies can change outcomes without changing the underlying reciprocity rule.
54. Problem-shifting and rolling stewardship burden belong in the world contract; a green-looking solution can still export costs across sectors, regions, time, or successor maintenance obligations rather than genuinely reducing intergenerational burden.
55. Own-lifetime payoff boundary and temporal policy discounting belong in the world contract; payoffs arriving within life, near the lifespan edge, or mainly after death are different institutions, especially when caregiver or descendant cues lengthen personal time horizons.
56. Significant-harm floors, tipping points, and triggered revision rights belong in the world contract; hard no-go thresholds and explicit switch / review triggers are different institutions from smooth average-welfare management.
57. Representative source, selection route, and cohort composition belong in the world contract; incumbent officeholders, youth, affected communities, experts, ombuds, and sortition samples are different proxy institutions even when formal powers are held fixed.
58. Permanence, institutional anchors, and cross-cycle memory belong in the world contract; one-off consultations, periodic forums, permanent councils, and anchored institutions with mandatory response paths are different institutions rather than administrative packaging.

## What To Build First

1. Dual-solver SMT lane (`Z3` + `cvc5`) over a shared SMT-LIB emitter.
2. Cross-solver agreement and divergence artifacts as gating evidence.
3. Holdout robustness suite expansion (noise, horizon, opponent-shift, and extortion/fairness pressure).
4. Anti-vampire scorecards that track payoff asymmetry, recovery, and repair-channel abuse.
5. One compact strategy-space frontier check (memory-one vs richer/simpler adjacent spaces) as a standing benchmark.
6. One noisy voluntary-repetition benchmark slice so fixed-dyad retaliatory classics are re-tested after leave/rematch exists.
7. One disclosed-action / leader-follower benchmark slice kept separate from simultaneous-play claims.
8. One minimal partner-choice measurement split that records observable help separately from hidden partner-maintenance help.
9. One minimal reputation lane with explicit public/private assessment and update-rule metadata.
10. One minimal reputation lane that separates sparse observation from fading / `Unknown` states and checks whether punishment changes the conclusion.
11. One minimal gossip-enabled companion lane with explicit cadence / fan-in / trust-weight metadata compared against a no-gossip baseline.
12. One minimal sanction / exclusion companion lane with explicit rehabilitation / re-entry metadata.
13. One repair-signal comparison with published signal rights, no-signal baseline, and follow-through / abuse metrics.
14. One richer reputation companion lane with declared reputation alphabet / transition granularity and one binary baseline.
15. One bounded-memory trust companion lane with explicit record-retention / rehabilitation-countdown semantics.
16. Typed Rust-to-Python FFI for certification-critical functions.
17. Claim schema enforcing evidence-class tagging in reports.
18. One hybrid human/AI companion lane with explicit agent-type assessment metadata and a human-only baseline.
19. One hybrid reputation companion lane with declared reputation-scope / spillover semantics and a no-class-spillover baseline.
20. One group-structured reputation companion lane comparing individual-only assessment against collective or stereotype-enabled assessment.
21. One intergroup reciprocity companion lane with explicit competition and cross-boundary-enforcement / mobility metadata.
22. One minimal reputation-governance companion lane with declared synchronization / consensus topology and a mostly-private baseline.
23. One centralized-score caution lane with declared direct-experience override and score-repair semantics.
24. One monitoring-economics companion lane with explicit observation-cost / cadence and evidence-transfer-friction metadata.
25. One helping-evaluation companion lane with explicit willingness-versus-ability and recipient need / burden semantics.
26. One inequality-source companion lane with explicit endowment / productivity / merit-versus-luck metadata.
27. One scarce-allocation companion lane comparing automatic allocation against planner or third-party allocation with declared rule semantics.
28. One sanction-metanorm companion lane with declared admissible observer responses and explicit non-enforcement / anti-social-punishment treatment.
29. One enforcer-governance companion lane comparing an unaudited nonprofitable sanctioner baseline against monetized, retaliation-exposed, or higher-order-monitored sanctioners.
30. One stochastic-risk companion lane comparing idiosyncratic shock exposure against shared-shock / common-fate exposure with declared pooling and payout-timing semantics.
31. One fallback-institution companion lane comparing informal-aid-only worlds against optional or automatic formal-insurance worlds with declared eligibility and crowd-out semantics.
32. One concurrent-portfolio companion lane comparing a single-channel baseline against same-partner and different-partner concurrent worlds with declared lane salience.
33. One cross-lane-linkage companion lane comparing channel-isolated memory against intentionally linked or crosstalk-prone concurrent worlds.
34. One encounter-topology companion lane comparing a well-mixed or degree-neutral baseline against clustered, hub-skewed, or degree-assorted networks with declared bridge / hub metrics.
35. One tie-formation companion lane comparing forced mixing or no-homophily against homophily-enabled or selective-separation rewiring with declared prior-acquaintance and tie-dissolution semantics.
36. One harm-accounting companion lane comparing help/provision against harm/prevention framing, with declared gain/loss sign structure.
37. One collective-damage companion lane comparing immediate harm against delayed harm and certain thresholds against uncertain or weakest-link thresholds.
38. One triadic or other small-group companion lane comparing a dyadic baseline against explicitly linked three-person interdependence with declared third-player position and information-scope semantics.
39. One delegated-coordination companion lane comparing no delegation against partial-voice, coalition-stage, or representative-selection worlds with declared leader / representative selection rules.
40. One private-solution companion lane comparing no-private-option worlds against mixed public/private-solution worlds with declared access asymmetry and relative efficacy.
41. One outside-option semantics companion lane comparing fixed-group or high-loner-externality worlds against flexible-group / low-loner-externality worlds.
42. One successor-binding companion lane comparing fully revisable successor worlds against time-limited, multi-step, or escape-enabled commitment worlds with declared lock duration and override cost.
43. One future-beneficiary-representation companion lane comparing no-proxy / universal-beneficiary worlds against guardian, future-design, or socially narrowed future-beneficiary worlds with declared representation powers.
44. One future-generation-depth companion lane comparing near-horizon and far-horizon beneficiary worlds with declared cohort-distance semantics.
45. One future-vividness companion lane comparing a low-link / low-vividness baseline against an intertemporally linked or psychologically proximal future-beneficiary world with declared agency semantics.
46. One positive-future companion lane comparing neutral, utopian, and efficacy-rich future visions with declared desirability / achievability / emotional-benefit semantics.
47. One distress-channeling companion lane comparing low-scaffold future-burden worlds against meaning-focused or agency-supported variants with declared action-channel and follow-up semantics.
48. One present-versus-future costly-help companion lane comparing matched-cost present-beneficiary, future-beneficiary, and mixed-beneficiary worlds with declared sacrifice semantics.
49. One fairness-reference-group companion lane comparing household/local, vulnerable-subgroup, societal, and future-generation fairness framings under matched aggregate payoffs.
50. One descendant-specific-beneficiary companion lane comparing abstract future people against children/grandchildren or caregiver-activated beneficiary worlds under matched costs.
51. One intergenerational-dialogue companion lane comparing one-way instruction, youth-led dialogue, and reciprocal exchange with declared voice symmetry and contact cadence.
52. One future-voice companion lane comparing no-voice, future-design, soft-advice, and stronger throughput-accountability worlds with declared representation powers.
53. One rolling-stewardship companion lane comparing low-maintenance / passive-safety worlds against open-ended successor-stewardship worlds with declared sectoral / geographical / temporal problem-shift metrics.
54. One deliberation-versus-teeth companion lane comparing seat-rich / low-power, deliberation-rich / advisory, and empowered-watchdog worlds with declared audit, agenda, delay, veto, or override powers.
55. One value-pluralism companion lane comparing single-objective / locked-future worlds against laddered or portfolio / option-preserving worlds with declared value-uncertainty and successor-revision semantics.
56. One lifespan-boundary companion lane comparing within-lifetime, edge-of-lifetime, and beyond-lifetime payoff arrival under matched aggregate benefits with declared time-horizon activation semantics.
57. One threshold-and-trigger companion lane comparing smooth-tradeoff worlds against significant-harm-floor / trigger-driven pathways with declared indicators, review rights, and switch authority.
58. One representative-source companion lane comparing youth, affected-community, expert-appointed, incumbent, and randomly selected future proxies under matched formal powers and declared contestability rules.
59. One permanence-and-anchor companion lane comparing one-off, periodic, permanent, and sunsetted future-facing institutions with declared anchor agency, knowledge-transfer, and mandatory-response semantics.

Why this order:
- It strengthens correctness posture before expanding search breadth.
- It creates fast feedback for solver or semantics regressions.
- It avoids false confidence from leaderboard-only workflows.

## What To Avoid (For Now)

1. Do not launch large-scale evolutionary search before formal claim classes exist.
2. Do not make PRISM/STORM mandatory for all runs on day one; start with small stochastic worlds.
3. Do not chase many verification tools simultaneously as blocking dependencies.
4. Do not produce public “best strategy” claims without explicit failure envelope artifacts.
5. Do not let orchestration convenience bypass deterministic replay contracts.
6. Do not treat intergenerational sustainability gains as generic reciprocity evidence when successors were locked into preservation by design.
7. Do not treat future-facing cooperation gains as universal morality when absent beneficiaries only became legible because a proxy, guardian, or ingroup framing was added.
8. Do not treat future-facing gains as generic reciprocity evidence when the world quietly shortened beneficiary horizon or made future harms feel psychologically near by design.
9. Do not treat future-oriented gains as generic reciprocity evidence when the world made a positive future newly imaginable, achievable, or emotionally rewarding by design.
10. Do not treat future-facing worry or urgency as a monotone motivator when action channels, agency, or coping scaffolds changed at the same time.
11. Do not treat future-facing cooperation as evidence of neglecting the present when the world never measured matched-cost present-day helping beside future-oriented help.
12. Do not treat fairness-driven uptake as generic justice evidence when the benchmark quietly changed the reference group from household or local burdens to broad society or future generations.
13. Do not treat future-facing support as generic morality evidence when the policy simply moved benefits inside participants' perceived lifespan or activated longer personal time horizons.
14. Do not treat long-horizon protection as generic reciprocity evidence when the world added hard harm floors, tipping-point triggers, or mandatory review / switch rights rather than improving the base action norm.
13. Do not treat descendant-framed future concern as universal moral expansion when the benchmark only changed beneficiaries from anonymous future people to one's own children or grandchildren.
14. Do not treat intergenerational cooperation gains as generic reciprocity evidence when the benchmark only changed who could speak first, who could influence whom, or how much anti-ageism contact participants received.
15. Do not treat future-facing gains as generic reciprocity evidence when the world added future voice, advisory scrutiny, or ex-ante accountability machinery while holding the base action policy fixed.
16. Do not treat sustainable-looking solutions as generic Golden-Rule progress when they only shifted burdens across sectors, regions, time, or into rolling successor maintenance labor.
17. Do not treat future-representation gains as generic reciprocity evidence when the world only increased deliberative depth, stakeholder presence, or institutional teeth without changing the base cooperative problem.
18. Do not treat one guessed long-horizon solution path as future-protective by default when the world also fixed disputed successor values and reduced option value under uncertainty.
19. Do not treat future-facing gains as generic reciprocity evidence when the benchmark only changed who was allowed to speak for future beneficiaries — youth, affected communities, experts, incumbents, or sortition samples — while preserving the same generic 'future representation' label.
20. Do not treat long-horizon institutions as generically more future-regarding when their gains come from permanence, institutional anchors, mandatory response loops, or stronger cross-cycle memory rather than from any change in the base action norm.

21. Do not treat future-facing gains as generic reciprocity evidence when the world only added future-impact templates, explicit long-term trade-off accounting, written-response duties, or recurring audit / progress-report cycles while holding the underlying action problem fixed.
22. Do not treat long-horizon gains as generic morality evidence when the headline result is mostly driven by a lower or declining discount schedule, different capital treatment, or different demographic / future-bias assumptions in the valuation rule.
23. Do not externalize broad private repo slices to remote Rust tools just because the local toolchain is blocked; use remote compilers only for tiny self-contained snippets and keep the durable archive citation-first and minimal.

## 12-Week Priority View

### Weeks 1-2

1. Finalize claim taxonomy and solver obligation table in specs.
2. Implement SMT-LIB emitter and baseline solver adapters.
3. Add solver replay artifacts and agreement checks.

### Weeks 3-6

1. Expand holdout and robustness matrix suites.
2. Add claim-tagged report schema and verifier.
3. Add typed FFI path for certification-critical Rust kernels.

### Weeks 7-9

1. Pilot PRISM/STORM model-checking on one stochastic world family.
2. Add simulation vs model-checking bound comparison artifacts.
3. Add divergence triage flow and ledger integration.

### Weeks 10-12

1. Harden reproducibility bundle schema and independent verifier.
2. Calibrate strict formal checks for release mode.
3. Publish first source-backed scientific report bundle.

## Decision Gates

1. Promote solver checks from advisory to required only after cross-solver stability.
2. Promote model-checking from pilot to required only after bounded world templates stabilize.
3. Promote robustness claims to external reporting only after holdout coverage thresholds are met.

## Failure Conditions

If any condition appears, freeze expansion and repair foundations:

1. Cross-solver disagreement rate spikes without clear triage.
2. Replay failures occur for previously “green” claim bundles.
3. Robustness suite regressions are hidden by aggregate leaderboard summaries.
4. Assumption backlog grows without retirements across two cycles.
42. One institution-legitimacy companion lane comparing exogenous rule imposition against endogenous selection or voting with declared advisory / binding semantics.
43. One franchise-scope companion lane comparing complete all-member institutions against subgroup-binding or partial-franchise variants with declared electorate, threshold, and binding scope.

23. Do not treat future-facing gains as generic reciprocity evidence when the world only upgraded future beneficiaries from rhetorical concern to rights-holders, broadened standing, lowered enforcement barriers, or opened stronger remedy routes.
24. Do not treat long-horizon protection as generic Golden-Rule progress when the world mainly changed its precaution default, science threshold, or burden of proving safety under irreversible risk.
25. Do not treat future-facing gains as generic reciprocity evidence when the world mainly shifted from compensate-later repair to avoidance-first, non-substitutable loss rules, or larger-scale restoration order while holding the base action problem fixed.
26. Do not treat long-horizon prudence as generic morality evidence when the benchmark mainly changed its robustness / regret architecture — reference optimization versus no-regret, stress-tested, or adaptive-pathway design.

27. Do not treat long-horizon prudence as generic morality evidence when the benchmark mainly changed its staged-commitment architecture — one-shot lock-in versus pilot, temporary-experimental, or reversible trial design.
28. Do not treat future-facing durability as generic reciprocity evidence when the benchmark mainly changed expiry, reauthorization, or policy-stock retirement semantics, or simply kept implementation load below overload / triage thresholds.


29. Do not treat future-facing prudence as generic reciprocity evidence when the benchmark mainly shifted from unfunded successor liability to prefunding, bonding, reserve segregation, conservative cost estimation, or stronger financial assurance.
30. Do not treat long-horizon stewardship gains as generic reciprocity evidence when the benchmark mainly made condition decline, depreciation, and deferred-maintenance backlogs legible and governable rather than morally transformed.
34. Do not treat long-horizon stewardship gains as generic reciprocity evidence when the world merely delayed assurance release, lengthened monitoring windows, or added conditional-closure / periodic-review machinery.
35. Do not treat successor protection as generic Golden-Rule progress when the world mainly changed residual-liability transfer, parent / pooled backup, or taxpayer-backstop semantics under insolvency or abandonment.
36. Do not treat long-horizon trust or stewardship gains as generic reciprocity evidence when the benchmark mainly changed who could independently verify claims, inspect evidence, challenge findings, or trigger reassessment.
37. Do not treat deep-time durability as generic future regard when the benchmark mainly changed the intelligibility, renewal cadence, dispersal, or re-openability of records handed to future stewards.
38. Do not treat deep-time durability as generic future regard when the benchmark mainly changed successor competence continuity — staffing depth, overlap, training, geographic placement, or mission-critical knowledge retention.
39. Do not treat long-horizon resilience as generic reciprocity evidence when the benchmark mainly changed whether roles, interfaces, and contingencies were rehearsed through drills, exercises, and after-action correction rather than merely written down.

40. Do not treat long-horizon durability or successor-friendliness as generic reciprocity evidence when the benchmark mainly changed interoperability, open-standard support, export fidelity, persistent identifiers, or practical vendor-exit optionality.
41. Do not treat long-horizon resilience as generic reciprocity evidence when the benchmark mainly changed graceful-degradation promises, manual fallback, alternate processing paths, or backup communications / interface architecture.


42. Do not treat long-horizon durability or authenticity as generic reciprocity evidence when the benchmark mainly changed fixity-refresh cadence, repair duty, format-risk review, or preservation-action planning rather than the underlying action norm.
43. Do not treat successor-safe trust as generic Golden-Rule progress when the benchmark mainly changed crypto agility, algorithm-transition readiness, or validation / monitoring of cryptographic migration rather than the underlying cooperative problem.
44. Do not treat successor-safe trust or provenance as generic Golden-Rule progress when the benchmark mainly changed trust-anchor rotation windows, signer / delegation thresholds, or out-of-band recovery paths rather than the underlying cooperative problem.
45. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed append-only transparency logging, proof-verifiable inclusion / history, monitor coverage, or transparency-service plurality rather than the underlying cooperative problem.
46. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed checkpoint witnessing, witness quorum, configuration-governed witness plurality, client self-audit, or gossip-based split-view detection rather than the underlying cooperative problem.

47. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed expiry windows, securely attested time, publication-latency / freshness bounds, timestamp renewal, or renewable evidence maintenance rather than the underlying cooperative problem.
48. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed whether verification materials were retained in portable bundles / receipts, whether trust roots survived locally, or whether claims remained verifiable after original services disappeared rather than the underlying cooperative problem.
49. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed verifier-policy snapshots, accepted signer identities / trust roots, claim-check strictness, or deterministic appraisal profile semantics rather than the underlying cooperative problem.
50. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed revocation / suspension semantics, status freshness, unknown-status fallback, supersession / end-of-life routing, or compromise-time interpretation rather than the underlying cooperative problem.
51. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed immutable subject identifiers, tag / URL mutability, digest pinning, or resolver-independent attachment / alias-correlation semantics rather than the underlying cooperative problem.

52. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed canonicalization boundary, deterministic-serialization rules, payload-type binding, or which representation transforms preserve verification rather than the underlying cooperative problem.

53. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed media-type tagging, predicate / schema identity, context pinning, vocabulary continuity, or unknown-term handling rather than the underlying cooperative problem.

54. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed issuer standing, delegated role scope, namespace custody, workload-registration selectors, or audience restrictions rather than the underlying cooperative problem.
55. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed threshold / quorum rules, the unit of distinctness that counts toward threshold, separation-of-duty assumptions, witness quorum, or multi-service concurrence policy rather than the underlying cooperative problem.
56. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed delegation priority, terminating or veto semantics, agreement-versus-mere-count requirements, issuer-inclusion policy, AND-vs-OR policy composition, or no-match fallback behavior rather than the underlying cooperative problem.

57. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed whether final verdicts ship with determining-policy diagnostics, explanation traces, decision / request ids, obligations / advice, or verifier-build / bundle provenance rather than the underlying cooperative problem.

58. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed reference-value corpus, endorsement-set composition, trust-root refresh path, policy-data bundle contents, or missing-baseline fallback behavior rather than the underlying cooperative problem.

59. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed evidence-acquisition topology, freshness-handle / nonce binding, claim-selection scope, relay or broker trust assumptions, captured observation fields, or staged-capture boundaries rather than the underlying cooperative problem.

60. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed disclosure profile, derived-predicate versus raw-claim presentation, mandatory-versus-optional reveal rules, omission semantics for absent fields, holder-binding for forwarded disclosures, or verifier retention intent rather than the underlying cooperative problem.

61. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed verifier ask shape, alternative claim / credential combinations, submission-requirement logic, path-mapping witness, authorized-query boundary, or preferred-versus-fallback satisfaction route rather than the underlying cooperative problem.
62. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed intended-verifier targeting, `client_id` / audience / origin checks, session nonce or wallet-nonce binding, authenticated session-transcript / handover rules, route or method binding, or replay acceptance window rather than the underlying cooperative problem.
63. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed discovery mode, trust-chain evaluation, metadata-policy application, resolved endpoint / keyset / algorithm surface, signed-versus-unsigned metadata posture, cache / version state, or invalid-metadata fail-closed behavior rather than the underlying cooperative problem.
64. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed chosen format / proof / algorithm / response-mode profile, request- or response-encryption posture, explicit typing / protected-request mode, or downgrade / unsupported-capability rejection semantics rather than the underlying cooperative problem.
65. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed authenticator class, user-presence or user-verification requirements, device-bound versus syncable key posture, attestation richness, or holder-binding-required versus holder-binding-waived semantics rather than the underlying cooperative problem.
66. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed transaction-specific binding, `authorization_details` specificity, granted-subset semantics, request-object signing / encryption, pushed-request tamper resistance, or approval-object comparison rules rather than the underlying cooperative problem.

67. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed identifier stability, sector-pairwise versus globally stable pseudonyms, proof-family linkability, issuer / type leakage posture, status-check observer surface, or omission-padding / decoy privacy rather than the underlying cooperative problem.

68. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed front-channel versus backchannel request transport, signed/encrypted request posture, redirect-versus-body response mode, response encryption, browser-history or query exposure, or which intermediaries could observe plaintext rather than the underlying cooperative problem.
69. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed what the user actually saw: claim label or field ordering, locale / formatting, trusted browser or wallet chrome versus merchant-controlled rendering, user-activation or explicit-intent ceremony, clickjacking resistance, or backend-versus-rendered transaction mismatch checks rather than the underlying cooperative problem.

70. Do not treat successor-safe provenance or authenticity as generic Golden-Rule progress when the benchmark mainly changed same-device versus cross-device ceremony split, QR versus deep-link versus targeted-app invocation, claimed-HTTPS versus custom-scheme dispatch assurance, or the presence versus absence of explicit proximity / cross-channel participation evidence rather than the underlying cooperative problem.

71. Do not treat a successor-safe ceremony receipt as inheritor-ready merely because it passes structural schema validation; if it still omits explicit verifier or audience binding, live-session or replay binding, request-integrity posture for by-reference asks, `direct_post` session-mapping material, or cross-device participation evidence, the archive has preserved shape without preserving the anti-phishing contract.

72. Do not treat warned or failed successor-safe ceremony receipt assessments as self-explanatory archive state; unless the archive also records an explicit disposition saying whether the receipt is claim-ready, provisional, or held for remediation — plus the required actions — future stewards inherit unresolved findings without custody of the actual risk response.

73. Do not treat a successor-safe ceremony receipt disposition as complete archive custody when it still leaves the repair path implicit; unless the archive also records a compact remediation plan with closure criteria and evidence paths, future stewards inherit the warning or fail label without the minimal map for getting back to claim-ready citation.
74. Do not treat a successor-safe ceremony receipt as finally claim-ready merely because it has a locator, an assessment, and a remediation plan; unless the archive also records an explicit authorization decision with basis checks and terms for continued citation, future stewards inherit the repair package without the final admission verdict.
75. Do not treat a successor-safe ceremony receipt package as newly claim-ready merely because the latest authorization is green; unless the archive also records a compact promotion record showing which prior non-pass findings closed, which findings carried or reopened, and why authorization changed, future stewards inherit the verdict without the closure basis.
76. Do not treat a successor-safe ceremony receipt package as indefinitely claim-ready merely because one past authorization turned green; unless the archive also records a compact review watch with reviewed-on date, reopen triggers, and a no-later-than review interval, future stewards inherit the verdict without custody of when it went stale.
77. Do not treat a successor-safe ceremony receipt package as still claim-ready merely because a review watch exists; unless the archive also records a compact review verdict for the actual as-of date and observed trigger state, future stewards inherit the freshness rule without the explicit keep-citing versus reopen-now decision.
78. Do not treat a successor-safe ceremony receipt review verdict as the final inheritor-facing freshness artifact; unless the archive also records a compact citation advisory saying what happens to existing citations and new citations, future stewards inherit the freshness judgment without the downstream keep-versus-withdraw handling decision.
79. Do not treat a successor-safe ceremony receipt citation advisory as the final inheritor-facing custody artifact if package membership still lives only in filenames and local browsing; unless the archive also records one compact package manifest naming the authoritative component set and their file-level fixity, future stewards inherit the downstream citation decision without a stable root for the package it referred to.
80. Do not treat a successor-safe ceremony receipt package manifest as the final package-root artifact if later freshness or repair work can replace it; unless the archive also records one compact supersession record naming which current manifest replaced the prior one, future stewards inherit fixity without an explicit replacement target.


81. Do not treat pairwise successor-safe ceremony receipt package supersession records as sufficient long-run custody once more than one refresh exists; unless the archive also records one compact lineage object naming the current authoritative head and the ordered chain behind it, future stewards inherit replacement facts without a stable answer to which package root is authoritative now.

82. Do not treat a successor-safe ceremony receipt package lineage as the final discovery artifact once it exists; unless the archive also records one compact package-head pointer naming the current authoritative manifest and its live status artifacts with standard relation semantics, future stewards inherit the authority chain without the cheapest answer to where the live package root is right now.

83. Do not treat a successor-safe ceremony receipt package head as the final inheritor-facing status artifact once it exists; unless the archive also records one compact package-status card collapsing the live review window, as-of review verdict, citation guidance, and current citable result, future stewards still have to open multiple neighboring files just to answer whether the head remains safe to cite right now.

84. Do not treat a successor-safe ceremony receipt package-status card as the final inheritor-facing redirect artifact once superseded package roots remain in the archive; unless the archive also records one compact package-redirect object using registered relation semantics to point a steward from the superseded manifest to the preferred current package-reference target and live status resource, future stewards inherit current-state facts without the cheapest answer to what replaces the older package root.

85. Do not treat a set of successor-safe ceremony receipt package heads and redirects as a sufficient archive discovery surface once more than one package family or superseded package root exists; unless the archive also records one compact package catalog listing the live heads and retained redirects, future stewards inherit correct local artifacts without the cheapest answer to what package roots currently exist and which one to open first.

86. Do not treat a successor-safe ceremony receipt package head as fully self-explanatory merely because it names the current manifest and status card; unless the archive also records one compact package verification report saying which local checks actually ran and where the cloudtainer boundary stopped, future stewards inherit the live package root without custody of the verification basis behind it.

87. Do not treat a successor-safe ceremony receipt package verification report as the final inheritor-facing verification artifact; unless the archive also records one compact package claim-scope object saying which downstream claims the current local verification basis supports and which remain out of scope, future stewards inherit the check results without custody of how not to overstate them.

88. Do not treat a successor-safe ceremony receipt package status card, verification report, and claim-scope artifact as a sufficient inheritor-facing use surface merely because all three exist; unless the archive also records one compact package reliance card collapsing the current citable posture, local verification basis, allowed claim classes, restricted claim classes, and required qualifiers, future stewards still have to reconcile several neighboring artifacts before knowing what they may safely rely on right now.
