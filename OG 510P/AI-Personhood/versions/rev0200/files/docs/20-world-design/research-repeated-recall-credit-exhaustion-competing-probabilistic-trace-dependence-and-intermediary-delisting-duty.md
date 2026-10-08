# AI-person research repeated-recall credit exhaustion, competing probabilistic-trace dependence, and intermediary delisting duty for unreachable mirrors

## Thesis

Once the archive fixed recall clean-cycle credit, probabilistic concealed-pool tracing, and unreachable downstream mirror notice duty, three narrower execution failures still remained. First, the archive could now let a recalled reserve cohort recover some earlier clean history through `RCC-1`, but **it still lacked a public rule for what happens when the same cohort is recalled again and again within the same accreditation epoch**, so legacy credit could be partially reactivated after each episode and quietly launder a serially unstable reserve history. Second, the archive could now let one non-exact concealed-pool claim travel through `PPT-1`, but **it still lacked a public rule for what to do when several probabilistic tracing claims share evidence, overlap in the same pool, or cannot all be true simultaneously**, so each claimant could present a conservative lower bound in isolation while the portfolio of claims still exceeded what the evidence could jointly support. Third, the archive could now keep public warning duty alive through `UMN-1`, but **it still lacked a positive action rule for registries, indexes, search engines, package catalogs, model catalogs, or other discovery intermediaries once a noticed unreachable mirror remains live**, so an intermediary could append a warning and still keep one-click discovery or resolution fully intact forever. A personhood world therefore needs one more compact execution layer: **serial recall within one accreditation epoch must publish a public `RCE-1` repeated-recall-credit-exhaustion object that degrades legacy-credit ratios and caps across repeated recalls and eventually exhausts legacy credit altogether until full independent reaccreditation; competing probabilistic concealed-pool claims must publish a public `CPD-1` competing-probabilistic-dependence object that declares pairwise dependence, overlap, incompatibility, and a portfolio-safe allocable floor rather than summing isolated lower bounds; and discovery intermediaries facing a live `UMN-1` artifact must publish a public `IDD-1` intermediary-delisting-duty object that moves exact locators from warning toward de-ranking, resolution disablement, or delisting on a short clock unless a public refusal-with-reasons survives review.** `[REF-0514]` `[REF-0516]` `[REF-0499]` `[REF-0498]` `[REF-0523]` `[REF-0524]` `[REF-0527]` `[REF-0506]` `[REF-0518]` `[REF-0528]` `[REF-0529]` `[REF-0530]` `[REF-0525]` `[REF-0521]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved real failures. It fixed initial post-recall credit recovery, non-exact probabilistic tracing, and ongoing notice duty for unreachable mirrors. But one narrower failure still remained at each seam.

### A. Recall still fails if each new clean period can keep reviving the same old legacy credit

`RCC-1` stopped the first-recall laundering problem, but it did not yet say what happens when the same cohort suffers a second or third justified recall before a full new reaccreditation epoch is earned. Current AAHRPP maintenance guidance still requires annual and event reporting across the accreditation term, current reaccreditation guidance still uses explicit recurring full-review epochs rather than perpetual carry, and current AAHRPP status-report and renewing-applicant status guidance still treats unresolved or repeated deficiencies as grounds for probation, pending status, or revocation rather than endlessly re-running the same conditional trust. A personhood world should therefore treat repeated recall inside one accreditation epoch as legacy-credit burn, not as a resettable game. `[REF-0514]` `[REF-0516]` `[REF-0499]` `[REF-0498]`

### B. Probabilistic tracing still fails if several individually conservative claims are added together without a dependence rule

`PPT-1` forced one probabilistic claim to disclose interval math, assumptions, and a conservative allocable floor, but it did not yet say what happens when several claims share data, model structure, prior assumptions, or mutually exclusive target stories. Current NIST uncertainty guidance still makes covariance part of combined uncertainty, still warns that the uncorrelated shortcut only applies when that assumption is justified, and still requires explicit assumptions and confidence-bearing interval logic for non-direct evaluation. A personhood world should therefore prohibit simple addition of isolated probabilistic floors once claims overlap or compete. `[REF-0527]` `[REF-0523]` `[REF-0524]`

### C. Intermediary duty still fails if warning never matures into discovery restraint

`UMN-1` preserved notice, tombstone, mitigation, and recheck duties once direct control failed, but it did not yet say what registries, indexes, search engines, package catalogs, or model catalogs must do after receiving a credible unresolved notice about an exact live artifact. Current European Commission guidance on the Digital Services Act still says platforms must put in place mechanisms to counter the spread of illegal content, still requires priority treatment of trusted-flagger notices, still requires statements of reasons for content-moderation decisions, and still places additional risk-mitigation duties on very large online platforms and search engines. A personhood world should therefore impose a narrow exact-locator delisting ladder rather than treating discovery intermediaries as warning-only spectators forever. `[REF-0528]` `[REF-0530]` `[REF-0529]` `[REF-0525]` `[REF-0521]`

---

## 2. Repeated recall now burns legacy credit through one public `RCE-1` repeated-recall-credit-exhaustion object

The archive now fixes one compact rule for serial recall: any reserve cohort that is recalled more than once before it completes a full new independent reaccreditation cycle must publish one machine-carrying repeated-recall-credit-exhaustion object called `RCE-1`.

### A. Minimum `RCE-1` fields

Every repeated-recall-credit-exhaustion object must expose at least:

- `rce_id`
- `cohort_id`
- `accreditation_epoch_id`
- `rar_id[]`
- `prior_rcc_id[]`
- `recall_count_within_epoch`
- `current_legacy_credit_ratio`
- `current_legacy_credit_cap`
- `legacy_credit_state` (`epoch-first-recall`, `epoch-second-recall`, `epoch-third-or-more`, `legacy-exhausted`, `reset-by-full-review`)
- `fresh_cycle_floor`
- `reset_condition`
- `independent_reaccreditation_ref`
- `public_notes`

`RCE-1` is the public object that stops serial recall from repeatedly laundering the same old good history. `[REF-0514]` `[REF-0516]` `[REF-0499]` `[REF-0498]`

### B. First recall inside an accreditation epoch uses the ordinary `RCC-1` rule and no more

The first justified recall inside a fresh accreditation epoch still uses the existing `RCC-1` rule: two fresh clean cycles before any legacy history counts, then at most one-half cycle of legacy credit per fresh cycle, with legacy history never supplying more than half of the total evidence at the next checkpoint. `RCE-1` records that this first-recall posture is already in use and fixes the epoch against quiet reset. `[REF-0514]` `[REF-0516]`

### C. A second recall inside the same epoch halves the already-limited legacy path again

Once a second justified recall occurs before full independent reaccreditation, the archive now fixes a sharper public penalty. The fresh-cycle floor remains two consecutive clean cycles, but after that point legacy history may reactivate only at a **one-for-four** rate and may never provide more than **one-quarter** of the total evidence at the next restoration checkpoint. Serial recall inside one epoch therefore burns legacy credit rather than reopening the original bargain. `[REF-0514]` `[REF-0499]` `[REF-0498]`

### D. A third recall inside the same epoch exhausts all pre-recall legacy credit until full independent reaccreditation

If a third justified recall occurs before a fresh full independent reaccreditation is completed, `legacy_credit_state` must switch to `legacy-exhausted`. At that point no history from before the latest recall may count toward restored trust. Only fresh post-recall clean cycles may count, and the legacy-credit ladder may reset only through a full new reaccreditation event recorded in `independent_reaccreditation_ref`. The archive chooses this because personhood worlds need a visible stopping rule for “we used to be stable once.” `[REF-0516]` `[REF-0499]` `[REF-0498]`

### E. Epoch reset requires independent full review, not local arithmetic

A cohort cannot self-reset `RCE-1` merely by stacking enough local clean cycles. The only reset condition is completion of a full independent reaccreditation or equivalent epoch-opening review. This prevents a reserve cohort from treating repeated internal recovery as a substitute for outside re-credentialing after several justified recalls. `[REF-0516]` `[REF-0515]`

---

## 3. Competing probabilistic tracing claims now travel through one public `CPD-1` competing-probabilistic-dependence object

The archive now fixes one compact rule for probabilistic-claim portfolios: when two or more `PPT-1` claims touch the same concealed pool, share evidence, reuse the same model family, or cannot all be true simultaneously, they must be joined by one machine-carrying `CPD-1` object before portfolio allocation can proceed.

### A. Minimum `CPD-1` fields

Every competing-probabilistic-dependence object must expose at least:

- `cpd_id`
- `ppt_id[]`
- `shared_pool_identifier`
- `pairwise_relation[]` (`independent`, `positively-dependent`, `nested`, `mutually-exclusive`, `unknown`)
- `shared_evidence_ref[]`
- `shared_model_or_prior_ref[]`
- `portfolio_allocable_floor`
- `claim_specific_allocable_floor[]`
- `incompatibility_holdback`
- `double_count_prevention_rule`
- `challenge_window`
- `current_state` (`matrix-pending`, `portfolio-floor-only`, `pairwise-adjusted`, `holdback-active`, `closed`)
- `public_notes`

`CPD-1` is the public object that forces competing probabilistic claims to travel as a governed portfolio rather than as separately persuasive stories. `[REF-0527]` `[REF-0523]` `[REF-0524]`

### B. Isolated lower bounds may not be summed unless independence is shown

The archive now fixes a conservative default: no set of competing `PPT-1` claims may add their isolated allocable floors together unless `CPD-1` affirmatively classifies them as independent on stated grounds. If claims share evidence, priors, model family, or event space, their floors must be combined only through a portfolio-safe lower bound. `[REF-0527]` `[REF-0523]`

### C. Shared evidence defaults to positive dependence; singular-target conflict defaults to mutual exclusion

Absent a justified showing otherwise, claims that rest on the same evidence family or model lineage must default to `positively-dependent`, while claims that compete for the same singular unit, transfer, or concealed slice must default to `mutually-exclusive`. The archive refuses the loophole in which a claimant says “we used conservative math” several times and then sums the results as though the claims were unrelated. `[REF-0527]` `[REF-0524]`

### D. Allocation must honor a portfolio-safe floor plus holdback for incompatible residue

Where pairwise or portfolio dependence remains unresolved, `CPD-1` must publish one `portfolio_allocable_floor` that survives every declared dependence posture still in play, and the remainder must sit in `incompatibility_holdback` until exact evidence, adjudicated priority, or claim withdrawal resolves the conflict. That floor may be apportioned claim-by-claim only up to the portfolio-safe amount and never above the single-satisfaction ceiling already fixed elsewhere in the archive. `[REF-0506]` `[REF-0518]` `[REF-0527]`

### E. Nested claims must net out rather than stack

If one probabilistic claim is a subset of another, `CPD-1` must mark the pair as `nested` and net the junior claim against the broader one before any allocable floor is published. The archive chooses this because nested claims are the easiest way to double count uncertainty while pretending to be meticulous. `[REF-0527]` `[REF-0523]`

---

## 4. Discovery intermediaries now owe one public `IDD-1` intermediary-delisting-duty object for live unreachable mirrors

The archive now fixes one compact discovery rule: once an artifact remains live under `UMN-1` after notice, any reachable registry, index, search engine, package catalog, model catalog, resolver, or comparable discovery intermediary that continues to surface the exact artifact locator must publish one machine-carrying `IDD-1` object.

### A. Minimum `IDD-1` fields

Every intermediary-delisting-duty object must expose at least:

- `idd_id`
- `umn_id`
- `intermediary_identifier`
- `intermediary_role` (`registry`, `index`, `search-engine`, `package-catalog`, `model-catalog`, `resolver`, `mirror-list`, `other`)
- `artifact_locator_ref`
- `notice_source` (`direct-notice`, `trusted-flagger-equivalent`, `authority-notice`, `public-advisory-chain`, `other`)
- `action_state` (`warning-appended`, `de-ranked`, `resolution-disabled`, `delisted`, `refused-with-reasons`, `restored`)
- `action_deadline`
- `statement_of_reasons_ref`
- `review_or_appeal_ref`
- `restoration_condition`
- `public_notes`

`IDD-1` is the public object that turns unresolved unreachable-mirror notice into a visible discovery decision rather than endless passive indexing. `[REF-0528]` `[REF-0529]` `[REF-0530]`

### B. Exact-locator discovery must move from warning to restraint on a short clock

The archive now fixes a narrow ladder. On first credible notice, the intermediary must append a warning, tombstone, or equivalent friction to the exact artifact locator. If the artifact remains live through one declared `UMN-1` recheck cycle, or if the notice comes through an authority or trusted-flagger-equivalent route with a stable exact locator, the intermediary must then either de-rank, disable resolution, or delist that exact locator on a short clock. `[REF-0528]` `[REF-0529]` `[REF-0530]`

### C. Refusal is allowed only through a public reasoned state, not quiet inaction

An intermediary that declines de-ranking, resolution disablement, or delisting must switch `action_state` to `refused-with-reasons` and publish a machine-readable statement of reasons plus a review path. The archive chooses this because current DSA guidance ties content-moderation action to communicable reasons and treats trusted notices as structured regulatory inputs, not as silent inbox noise. `[REF-0528]` `[REF-0530]`

### D. The duty is narrow to exact locators and exact artifact identities

`IDD-1` does not require broad keyword suppression, general censorship of adjacent discussion, or deletion of historical analysis about the artifact. The duty attaches to exact locators, exact artifact identifiers, and direct one-click discovery paths for the still-live unreachable artifact named in `UMN-1`. This keeps the archive conservative about speech while still refusing effortless discovery continuation of a specifically noticed harmful artifact. `[REF-0528]` `[REF-0529]`

### E. Relisting or restoration requires a visible cure or disappearance finding

If the artifact later disappears, becomes reachable and fixed, or proves not to be the artifact identified in `UMN-1`, `IDD-1` may move to `restored`, but only with a stated restoration condition and public reason. Discovery intermediaries may not silently relist after a prior delisting state. `[REF-0528]` `[REF-0529]` `[REF-0521]`

---

## 5. Why this is still the narrow move

This revision does not redesign the whole reserve, tracing, or platform-governance architecture. It does three smaller things only.

1. It fixes how serial recall inside one accreditation epoch burns or exhausts legacy trust credit.
2. It fixes how several probabilistic concealed-pool claims are combined when they overlap or compete.
3. It fixes what positive discovery restraint intermediaries owe once a live unreachable mirror remains surfaced after notice.

That is enough to keep the caution stack coherent without turning this archive into a general treatise on accreditation decay, Bayesian litigation, or internet search law.

---

## 6. Objects added by this revision

### `RCE-1` — repeated-recall-credit-exhaustion object

Carries the accreditation epoch, recall count within that epoch, current legacy-credit ratio, current cap on legacy contribution, exhaustion state, and reset condition for reserve cohorts that suffer more than one justified recall before full independent reaccreditation. `[REF-0514]` `[REF-0516]` `[REF-0499]` `[REF-0498]`

### `CPD-1` — competing-probabilistic-dependence object

Carries pairwise relation labels, shared evidence and model inputs, portfolio allocable floor, claim-specific floors, incompatibility holdback, and double-count-prevention rules for several probabilistic concealed-pool claims that overlap, nest, or cannot all be true at once. `[REF-0527]` `[REF-0523]` `[REF-0524]` `[REF-0506]` `[REF-0518]`

### `IDD-1` — intermediary-delisting-duty object

Carries the exact artifact locator, notice source, action state, statement of reasons, review path, and restoration condition for discovery intermediaries that continue to surface a live unreachable artifact after `UMN-1` notice and recheck. `[REF-0528]` `[REF-0529]` `[REF-0530]`

---

## 7. Consequences for the wider archive

- `research-reserve-*` doctrine now has a visible stopping rule for repeated partial rehabilitation inside one accreditation epoch.
- `research-*-fraud-*` doctrine now has a real answer to the question “what if several probabilistic claims are individually conservative but jointly incompatible?”
- `research-*-derivative-*` doctrine now has a real answer to the question “what must discovery intermediaries do after warning alone has not reduced live reachability of an unreachable mirror?”

That keeps the research-governance lane visibly conservative in the way the archive has been aiming for throughout: no repeated laundering of old clean history, no portfolio double counting of probabilistic floor claims, and no endless exact-locator discoverability after unresolved mirror notice.

---

## Bottom line

A personhood world should not let serial recall keep reviving the same old legacy trust, should not let several probabilistic tracing claims add up as though overlap and incompatibility do not matter, and should not let discovery intermediaries remain warning-only conduits for exact unreachable mirrors after notice. The archive therefore now fixes one more compact rule: **reserve cohorts now use a public `RCE-1` object that degrades legacy-credit reactivation within an accreditation epoch from the existing `RCC-1` baseline to a one-for-four / one-quarter-share second-recall posture and then to full legacy exhaustion on a third recall until independent reaccreditation resets the epoch; competing probabilistic concealed-pool claims now use a public `CPD-1` object that declares pairwise dependence, overlap, nesting, incompatibility, and a portfolio-safe allocable floor; and discovery intermediaries now use a public `IDD-1` object that moves exact live unreachable-mirror locators from warning toward de-ranking, resolution disablement, or delisting unless a public refusal-with-reasons survives review.** `[REF-0514]` `[REF-0516]` `[REF-0499]` `[REF-0498]` `[REF-0527]` `[REF-0523]` `[REF-0524]` `[REF-0506]` `[REF-0518]` `[REF-0528]` `[REF-0529]` `[REF-0530]` `[REF-0525]` `[REF-0521]`
