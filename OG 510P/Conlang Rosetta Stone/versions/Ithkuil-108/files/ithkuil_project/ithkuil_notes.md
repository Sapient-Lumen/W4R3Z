# Notes / open issues (evolving)

## Versioning / resources
- We are using **New Ithkuil** resources (Lexicon v1.0 + Affixes list from ithkuil.net), while keeping `S«…»` carriers for technical or bespoke terms we are not lexicalizing yet.
- Goal: be “canonically accurate where possible”; when a direct lexical equivalent is unclear/absent, we preserve meaning by paraphrase and mark it.

## Style decisions (current)
- The essay’s technical definition **LOVE = goodwill** is encoded primarily as `NZ₂` (feeling/display of goodwill; benevolent intent/kindness), optionally moralized by `CB₁` (motive/reason‑why) + `ŘZ₂/₃` (disinterested probity/virtue) when the author’s normative load needs to be explicit.
- **COMMANDMENT / precept / rule** (A.0 biblical epigraph) is encoded as `RZ-OBJ` (law/precept to be obeyed), not older `TKH` placeholders.
- Romance/attachment “in love” is encoded only when clearly intended: `RKW₁`.
- Technical titles (THE GOOD / THE RIGHT / THE OTHER / DIALETHEIA / INFINIGRESS, etc.) remain as carriers until we decide to naturalize them.

## Migration note (root correction)
- Earlier archives briefly used `RTR₂` (and, once, an incorrect `ŢY₁`) as a proxy for “goodwill‑love”. The **New Ithkuil Lexicon v1.0** explicitly lists `NZ` as **GOODWILL / BEING NICE / BEING DECENT / GOOD SAMARITANSHIP**, and lists `RKW` for *affective* love (romantic / filial / love-for-abstraction). We are therefore standardizing on:
  - `NZ₂` for ethical “love = goodwill”
  - `RKW₁/₂/₃` only when the source is clearly talking about affective love states (e.g., “I love you” in a romantic sense).

## Recently corrected / pinned
- Existential “there is/are” uses `Ň₁` (not copular `Č`).
- “awareness / conscious noticing” pinned as `ŇJ` (usually stem 2).
- “understanding/comprehension” pinned as `VL`.
- “merit / deserve / reward” is **`KN`** (not `KM`).

## Open lexical gaps to resolve later
- “semblance / semblatic reflection” — currently `S«SEMBLATIC REFLECTION»`.
- “objective vs subjective” — currently `S«OBJECTIVE» / S«SUBJECTIVE»` unless we choose a cleaner grammatical strategy.
- “hedonic treadmill / desire-satisfaction cycle” — currently only partially built (`RP₃` + `B` (desire/need) + carrier).
- “contextually particularized” — currently a carrier modifier.

## 2026-01-20 — B.0.3 (moral motivation; maxims)

Pinned several previously-carrier concepts to canonical roots from roots‑v0.2:
- `CB` (“motive / intention”; FML1 = “principle/grounds/basis”) for “moral motivation” and “end/goal”.
- `CX` (“manner / behavior / method / policy”; FML2 = practice/policy) as the current best proxy for Kantian “maxim”.
- `ŘZ` (“disinterest / probity / honesty / virtue”) as the moral-qualifier for `CB` here.
- `ŢP` (“attribute / quality / intrinsic property”) + `SS` (“tool/means”) sketched as the working way to encode “end in itself (not as means)”.

Next pass for this sentence: pick a canonical “only” quantifier and choose an explicit predicate for “act on / apply to / operate only on”.

## 2026-01-20 — B.3.5 (risk→reward reduction claim)
- We now anchor “risk” and “payoff/reward” using **canonical affixes** rather than carriers:
  - `-PT-` (DNG) = degree of risk/danger.
  - `-FŢ-` (EFI) Stem 3 = degree of reward/value/payoff (return on investment).
- We still leave “neurochemical” as a carrier modifier and keep the “not merely” reduction strategy conservative until we decide whether to encode it via a dedicated evaluative/epistemic construction.

Update (Archive 103)
- Added a first explicit draft in `ithkuil_translation.md` treating “more than X” as “not *merely* X” (`NZ₂ ¬( Č₂  S«MERELY»  PT₁{PUR:FŢ₃{MOD:S«NEUROCHEMICAL» DOM:JV₁}} )`).

## Next targets in the source
- Continue after **B.3.7**: the paragraph beginning **“Within individuals, love is agape…”** (eros/philia/agape fusion; assent + self-creation; sublation; collective agents; cosmic recursion).
- Then: the remainder of the essay’s closing paragraph.

## New open issues from B.4.1–B.4.2
- Decide whether “Within individuals / within collective agents / cosmically” will consistently be **REF** (as-for) or **CNV** (contextual) framing.
- Find a dedicated root/stem for **VOLITION / will** (as a faculty/stance), distinct from `TÇ` “intentionality”.
- Decide how we will encode “sublation” once we stop using a carrier: pure `MC` “unify”, or a more explicit *synthesize/resolve-contraries* construction.
- Nail down the “toward/goal” encoding for “our will toward it” (likely an allative/goal case strategy once we choose a canonical case set).

## Next targets in the source (updated)
- Continue B.4 after **B.4.2**: “Love is both a morally justified cause and emergent consequence…”

## 2026-01-20 — B.4.3 (cause/result reciprocity)
- Using `GN` (source/origin/cause) to encode *emergence* (“come into being”) and/or *primary causation*.
- Using `ZẒ` (“binary polarity”) as a provisional stand‑in for philosophical “contraries/opposites”; revisit if we locate a root closer to *dialectical opposition* rather than literal polarity.
- For “cause” vs. “consequence”, we’re leaning on the **EFF** (Effectuative: enabler initiating a causal chain) and **RSL** (Resultative: consequence/result) cases from the New Ithkuil case system.

## 2026-01-20 — B.4.4 (collective-agent scale)
- Pinned `RMC₂` (unify) for the main predicate, with the “within collective agents” frame approximated via `D-CTE-REF`.
- Modeled “through/by means of …” via INS (instrumental/means).
- Encoded the paradox “forgivingly retaliating power” as `RMČ₁` (power) modified by `SŢ₁` (magnanimity/forgivingness) and `RŽ₂` (retaliatory capacity).
- Approximated “perspective decentralization” as `TÇV₁(RL₂)` (dispersion applied to viewpoint), flagged as metaphorical.

## 2026-01-20 — B.4.5 (cosmic recursion; inferential)
- Using **Validation = INF** as our canonical handle for “appears/seems”.
- Using **RSL** to encode “into X (as a result/outcome)” for “into harmonic flatness”.
- Pinned `ḐG` as our best “weave/interweave” analogue (inseparable intermixing) and `ŠH₃` as the canonical handle for “salient” (salience/prominence).
- Replaced earlier “contraries” placeholder (`ZẒ`) with `JŇ` when the text clearly means *opposition*; we may retro-fit B.4.3 later if that improves fidelity.

## 2026-01-20 — B.4.6 (subjective-context alignment)
- Using `ŢK₁` as the core “construction/configuration” predicate for LOVE.
- Using PUR (Purposive) to encode “toward / for the purpose of right relationship”, rather than forcing a spatial allative.
- Pinned `ÇŇ₂` (relate-to / relation) as the minimal lexical anchor for “relationship”.
- Leaving “subjective context” and “objective context of all contexts” as carriers for now, pending a decision on whether “objective/subjective/context” should be lexicalized or handled grammatically.

## 2026-01-20 — B.4.7 (moral mysticism)
- Pinned `VŽW` as the cleanest “mystical” handle in the intended *spiritual / transcendent / interconnected* sense (as opposed to superstition).
- Treating “morally” as a modifier grounded in `ĻD` (moral value/virtue/principle), likely via `ĻD‑CTE` when the modifier needs to behave like an adjectival property.
- Explicitly avoiding `ŘY₃` (mysticism as anti‑rational superstition) unless later text demands that negative sense.

## 2026-01-20 — B.4.1 (fitting + philia pinned)
- Pinned `RĻN₃` (fitting/apropos/suitable) for the “fitting” modifier.
- Swapped the earlier provisional philia handle (`DN‑FML₃`) to `LTW₃` (friendship/bond) as a cleaner canonical analogue.

## 2026-01-20 — Proem started (0.1.1–0.1.2)
- Began translating the opening italic paragraph as **Section 0** in `ithkuil_translation.md`.
- Chose to render “defines so much” as *importance/centrality* via `ŠH₁` within a REF-framed carrier `S«THE GREAT HUMAN CONVERSATION»`.
- Next to translate: 0.1.3–0.1.7 (“pick out the salience…”, “Consider the fall…”, “Suffer…”, “May we…”, “Joy…”) sentence-by-sentence.

## 2026-01-20 — Salience root pinned
- Replaced earlier provisional “salient = emphasis” handling with the canonical root **`ŠH`** (Stem 3 = salience/central significance).
- Updated B.4.5 and glossary accordingly.

## 2026-01-20 — Proem continued (0.1.3–0.1.5)
- Pinned `RNY-CSV` as the cleanest canonical handle for “pick out / single out / select” in 0.1.3.
- Used `Ž₁` (ability/capability) to render “as best I can” as a maximal-capacity adjunct.
- Used `SLB₂` for “consider” and `RŠ` (stage/phase; affix `STG`) to model “fall” as a constituent phase of “leap.”
- Added `MŢT₁` for “test/trial” in 0.1.5.
- Open lexical gap: find a good non-conflicting root/affix for “final/ultimate/culminating” so “final tests” isn’t left as a carrier modifier.
- Next to translate: 0.1.6 (“May we be worthy…”) and 0.1.7 (“Joy is…”) sentence-by-sentence.

## 2026-01-20 — Proem completed (0.1.6–0.1.7)
- Modeled “May we …” as a **aspirative framing** using **ASP modality** (Aspirative = wish/hope) whose *content clause* asserts 1P.PL worthiness.
  - Open issue: we may later prefer a dedicated **optative / hortative** illocution strategy once we re-check the most canonical way to render benedictions in New Ithkuil.
- For “what happiness we find”, chose `ŇV₂` (happiness) modified by a restrictive relative based on `PSS₁` (experience/perceive/live), i.e., “the happiness we experience/come upon”.
  - Open issue: there is a dedicated “find/encounter” root in the lexicon, but the text extraction we’re using currently omits the root label; revisit once we verify the missing glyph in the PDF.
- For “Joy is at least nearly selfless”, rendered the core as `ŇV₃` (joy) ≈ `VÇ₃` (charitableness/altruism/self-sacrifice; used here as our best 'selfless' proxy) with two degree placeholders: `S«NEARLY/ALMOST»` and `S«AT-LEAST»`.
  - Open issue: decide whether to encode these via **degree/gradation** (more compositional) or via dedicated **adjunct/affix** choices (if New Ithkuil offers a clean canonical equivalent for “at least” / “almost”).

## 2026-01-20 — Epigraph A.0 started (“The Greatest Commandment”)
- Treated “You shall …” as a **DIRECTIVE** illocution (command).
- For “with all your heart/soul/mind”, introduced **PTW/9** (VXCS affix) as our working “all/whole; entirely” quantifier, and used **INS** for the “with/by means of …” relation.
  - Open issue: locate canonical lexicon roots for HEART / SOUL / MIND in New Ithkuil so we can replace the current carriers.
- For “love your neighbor as yourself”, provisionally used **ASI (Assimilative) case** on SELF to encode “as/like yourself.”
  - Open issue: decide whether “as yourself” should instead be encoded via a similarity-level adjunct scoping the whole predicate.

## 2026-01-20 — Epigraph A.0.1 (1 Corinthians 13:4–7; trait bundle)
- Rendered the passage as a **bundle of trait predications** about `RTR₂` (ethical love/goodwill). (We keep earlier `ŠLW₂` as a deprecated proxy for patience/forbearance.)
- Revised the lead clause “patient” to `MSW₁` (tolerance) and rendered “kind” as `RKY₁` (warm/inviting/open‑hearted), while keeping `RTR₂` as the anchor for ethical love/goodwill.
  - Source for these emotion/trait roots: *ithkuil_iv_sensory_roots.pdf* (ithkuil.net)
- Pinned `ŘŘN₂` (jealousy; Stem 2 of the envy/jealousy family) for “jealous/envious.”
- Pinned `PSG₂` (conceit/being full of oneself) for “arrogant.”
- For “not easily provoked,” prefer `ŽŽV₂` (irritability / being easily-angered), leaving “easily” as a degree placeholder.
- For “keep an account of a wrong suffered,” pinned `KȚP₂` (holding a grudge / rancor / unforgiving) as the most direct canonical analogue.
- For “rejoices…,” pinned `LPY₁` (gladness/cheerfulness) contrasting content: ¬`LŽV₂-CTE` (absence of metaphysical justness) vs `RD₁-CTE` (truth/veracity).
- For the closing triad, used `MSW₃` (trusting) + **CRD modality** (believing) + `NTK₁` (hope) + `KTŘ₃` (endurance), each quantified by `PTW/9` over `S«ALL THINGS»`.
- Remaining open lexical gaps in A.0.1 are mostly *degree/adverbial* ones (e.g., “easily” in “not easily provoked”).


## 2026-01-20 — Epigraph A.1 (Aquinas: love as willing the good of the other)
- Treated the line as **definitional**: LOVE ≈ an intentional stance whose purpose is THE GOOD and whose beneficiary is THE OTHER.
- Provisional core strategy: `RTR₂-CTE  Č  TÇ-CTE` with a PUR-scoped `S«THE GOOD»` and BEN-scoped non-self personal referent `N{OBV}`.
- Left `S«THE GOOD»` and `S«THE OTHER»` as carriers pending a decision on whether we lexicalize these titles or keep them as technical terms.
- Open issue: whether the best handle for “will” is `TÇ-CTE` (intention) vs `NY₁` (choice) vs a causative “bring about” predicate.


## 2026-01-20 — Epigraph A.2 (Leibniz: pleasure in others’ happiness)
- Used `LPY₁` for “gladness/pleasure at another’s happiness or good fortune,” allowing a very compact rendering of the definition (“love = LPY₁”).
- Kept the expanded version as well (LPY₁ taking an explicit `ŇV₂{GEN:N{OBV.PL}}` object) for contexts where we want the stimulus to be overt.

## 2026-01-20 — Epigraph A.3 (cummings: “axis of the universe”)
- Chose `CL` as the cleanest canonical geometric stand‑in for “axis” as “central line / linear orientational middle.”
- Noted that the same semantics also exist as VXCS affix `-cl` (“linear uni-dimensional middle/center”), so the cummings line can be encoded either as a root-formative or as `NKR₃` carrying that VXCS affix.
- Chose `NKR₃` as “the World / external reality/universe.”
- Added an alternate metaphor: `ÇDR₂` “fulcrum/balancing point,” explicitly noting the lexicon’s requirement to mark this root as metaphorical when used figuratively.

## 2026-01-20 — Epigraph A.4 (Dostoevsky: “priceless treasure … redeem the world … cleanse sins”)
- Modeled “priceless treasure” via `ĻN-OBJ` (“something valuable”) plus a MAX/beyond-price scalar carrier.
- Used the deliverance/salvation family `CPR₂` as the best canonical handle for “redeem,” while flagging that the stem numbering in the text extraction is slightly ambiguous and should be re-verified against the PDF.
- Used `ZW₂` (purify / cleanse / decontaminate) for “cleanse.”
- Used `ḐẒ₂` (remain/retain long-term) adjectivally for “[what] remains (of the world).”
- Left “sin(s)” as a carrier pending a committed canonical moral-wrong strategy (candidates: `¬ŽV₂` vs `GŽŽ₁`, etc.).

- Epigraph A.9: treated “feels no burden” as positive comfort (`MMH₂`) rather than explicit negation; revisit if we decide on a dedicated ‘burden/onus’ lexical strategy.
- Epigraph A.10: mapped pejorative “Ego” to `ZČ₂` (selfish self-concern); used `RČ₃` for ‘reduce/lessen’ and `LŽV₁` as a provisional ‘equalize’ proxy.

## New open issues from B.0 (definition paragraph)
- Find/decide canonical roots (or compositional strategies) for:
  - **maxim** (Kantian practical principle), **motivation**, **commitment**, **responsibility**
  - **contingency** vs **necessity / necessitate**
  - **Moral Law** (could remain a carrier, but we may want an Ithkuil-native phrasing)
- Decide the best way to encode **“end in itself”**:
  - `PUR` (“as an end/purpose”) + `S«IN‑ITSELF/INTRINSIC»`, versus
  - an explicit contrast with `INS` (“means”) or a dedicated evaluative construction.
- Decide whether “possible world” should be:
  - a modal framing on `NKR₃` (“the World”) or
  - left as a technical carrier.

## Next targets in the source (current)
- Translate footnotes still missing: `p`, `tr`, `eu`.
- Revisit **A.4 Dostoevsky** once we pin “sin / wrongdoing” more canonically.

- Find/decide canonical roots/affixes for “predictability / identity-stability” and “idealize (person)” for footnote tr.


## New open issues (from 2026-01-20 continuation)
- Find a canonical New Ithkuil root/affix for **ostensive indication** (“point/indicate [at] X”) so we can replace the carrier `S«POINT / INDICATE»` in footnote C.2.
- Footnote **eu** has been started (C.8) but still needs to be expanded sentence-by-sentence; we’ll likely need a committed strategy for **PERSON vs non-person human** and for **prescriptive vs descriptive** justification/explanation.

## 2026-01-20 — Footnote C.8 (eu), sentence 2
- Added a draft for the “however unfair … evil agents … higher eudaimonia” sentence.
- Pinned `XhN₂` (existential irony/frustration/unfairness at morally flawed people thriving) as the concessive/attitudinal frame for “however unfair it may be.”
- Pinned `ŽV` (GOOD/BENEFICIAL; Stem 2 = morally right) as the canonical candidate for future replacements of `S«THE GOOD»` / moral-good predicates.
- Left open: a clean canonical root for EVIL, and a clean comparative-degree strategy (case-frame vs. adjunct) for “higher … than …”.

- B.2.5: Now anchored perceptibility via `ŠK` and generic “property” via `PÇK`; still need a canonical ostensive-indication root/strategy to replace `S«ONLY-POINT/INDICATE»`.
## 2026-01-20 — B.3.3 ("requirements of justification")
- Locked in `RT₃` for “meets requirements / satisfactory” (for “satisfies” in the justificatory sense).
- Locked in `MSK₁` for “requirement/necessity”, used to make explicit “requirements *of* justification”.



## 2026-01-20 — B.3.1–B.3.2 (eudaimonia / fulfillment / moral luck)
- Anchored “eudaimonia” as `SKY₁` (the canon “life-stance” root; close match to justified flourishing).
- Anchored “existential completion/fulfillment” as `ŘNY₁` (degree of emotional/intellectual fulfillment).
- Anchored “moral luck” using `LF₂` (fate/chance) scoped to the ethical domain (≈ `RLT:ŢŠ₂`).
- Began treating “moral virtue” via `BŇ₃` (degree of natural virtue / desired behavioral quality).

## 2026-01-26 — Canon refresh (CNJ/POT + ostensive indication)
- Confirmed via the official morphology/design docs that **CNJ Conjectural** is explicitly the illocution used for English-style “if”-clauses offered as conjectured hypotheticals, and that **POT** covers wishing/hoping statements.
- Pinned the lexicon root **`ŢČ`** (Stem 1) for “sign/signal/gesture/indication; to indicate/gesture/signal”, and swapped it in wherever we previously carried `S«POINT / INDICATE»`.

## 2026-01-28 — POT illocution + irwartfrr tokens

- Corrected earlier drafts that mislabeled “hope / may …” as *ASP modality*. In New Ithkuil, wishing/hoping is expressed via **POT (Potentiative) illocution**.
- Added working decompositions for the project tokens `S«irwartfrr»` / `S«irwrongfrr»`.
  - `irwartfrr` ≈ `EXT₆` (well enough / sufficiently exact manner) + `CPC₂` (having the opportunity / opportune circumstances) + `CB₁{ŘZ₂}` (right motive, with probity).
  - `irwrongfrr` ≈ `EXT₁/₂` + `CPC₁` + `CB₁{KNY₂/JD₁}` (ill‑fitting manner/time/motive).


## Newly pinned in this turn (v065→v066)
- VXCS affix **IDF/1** is now used for “whatever / any (of the various) X”.
- We are using **IRG** as the interrogative illocution label (per the official verb morphology documentation).
- For relative-clause restriction (“those maxims which …”) we are now marking the head formative with **DCD/5** (head of a relative clause).
- Corrected CB stem usage: **CB₁** = motive/reason‑why; **CB₂** = purpose/goal; **CB₃** = incentive/stimulus.


## ERRATA (root corrections)

- **EFFORT / attempt**: earlier drafts mistakenly used `XV` (compression/compaction). Correct handle is `RTM₂` (make an effort / do / act), optionally with affix `KP` to specify degree.


## Change log (recent)
- v070: corrected “readiness/preparedness” root usage: use `ÇL` consistently (removed stray `FS` mentions), and tightened B.2.1–B.2.2 with an explicit two‑clause draft.


## 2026-01-28 — B.2.3 present‑at‑hand vs. ready‑to‑hand (ŇL₂)

- Pinned **`ŇL₂`** (analytical reasoning/logic applied to figuring something out) as the best non‑computerish handle for the essay’s “present‑at‑hand computation”.
- For the Heidegger contrast:
  - “ready‑to‑hand” ≈ `MN₂` (default demeanor/temperament) + `ÇL` (readiness/preparedness) constructed by habituated procedures (`RCX₁`).
  - “present‑at‑hand” ≈ `FRM:KSL₂` (explicit analysis) + `MOD:ŇJ₂` (conscious awareness) applied to `ŇL₂` of `ŇŢ₂` (The Right).
## 2026-01-28 — B.4.4 (collective agents; unifying mechanisms)

- Drafted the first Ithkuil line for **B.4.4**, treating “within collective agents” as **domain/scale framing** and rendering “love is unifying” via `RMC₂`.
- Rendered the two stated mechanisms as **instrumental adjuncts**:
  - “forgivingly retaliating power” ≈ `RMČ₁<INS>{MNR:SŢ₁ MOD:RŽ₂}`
  - “perspective decentralization” ≈ `TÇV₁<INS>{OBJ:RL₂}` (RL kept as an approximate “subjective viewpoint” anchor for now).
- Updated glossary wording for `RMC₂` and `RMČ₁` to match the Lexicon v1.0 phrasing.


## Update log (2026-01-28)
- Tightened footnote **C.7 p** using `ŠK` (notice/see) + `ḐX` (utterance/text segment) for “you saw this line…”.
- Rewrote **C.8 eu** opening as an explicit negative existential skeleton; tightened the *can achieve* spine with `Ž₁` + `MBR₃` while leaving the comparative as a carrier.
- Glossary: clarified `TM₂` is not our “make an effort” root; `RTM₂` remains the effort/attempt handle.

## 2026-01-28 — Footnote C.8 eu completion (part 2)

- Added the missing parenthetical in C.8 (evil persons may be generally happier) using `ŇV₂` (happiness) plus `LÇ` (supposition) scoped by `RRJ₁` (assent/acceptance).
- Added the remaining C.8 line about **non-person flourishing without justification**, decomposed as: possibility + flourishing (`SMW₃` / optional `GḐ₁`) + ¬consider (`SLB₂`) + causal contrast between **OBG-framed** justification (`PJ`) and **descriptive** explanation (`RB`).
- ERRATUM: replaced the earlier mistaken “explain” handle `RBR`/`RBR₂` with canonical root `RB` (roots v0.2 list).

## 2026-01-28 — Footnote C.9 g (Goodwill unconditionally good)

- Chose `ŽV₂` (moral-goodness) as the predicate for “good” in Kant’s sense (good ‘in a metaphysical sense’). 
- Rendered “unconditionally / without qualification” via adverbial contrastiveness **CTR/4**: “conditions/qualifications notwithstanding / without taking X into account.”
- Draft line: `RTR₂-CTE  Č  ŽV₂-CTE  |  S«CONDITION / QUALIFICATION»{CTR₄}`.

- Canonicality check: in the v1.0 roots PDF, `NZ` is the explicit **GOODWILL / BEING NICE / BEING DECENT** root; `RTR` is the *feeling of* benevolence/helpfulness. We may want to migrate our project-wide `RTR₂`→`NZ₂` for “goodwill” later, keeping `RTR` for the affective layer.

## 2026-01-28 — v088
- Corrected footnote **b** “Baby don’t hurt me”: replaced mistaken `ČR` with canonical `RW` (HOSTILITY/AGGRESSION), and added stem-specific alternates.
- Marked early `C.3 g` sketch as deprecated in favor of the pinned `C.9 g` draft.


## 2026-01-28 — A.4 Dostoevsky (priceless treasure; redeem; cleanse)
- Added an explicit clausal draft for A.4 (Dostoevsky) with placeholders for scope items (PRICELESS, CAN/ABLE, NOT ONLY/BUT ALSO, SOME).
- Added the corresponding placeholder entries to the glossary.


## 2026-01-28 — v095
- Tightened **A.6 (Joyce)** into an explicit self-referential recursion: LOVE as subject enjoys the act of loving LOVE.
- Tightened **A.7 (MacDonald)** into two directive clauses using totality quantification; added carrier `S«PARADOXICALLY»`.

### Comparative strategy (Levels)

- When translating English comparatives (“more X than Y”, “higher degree of X than Y”), prefer **Level** operators on the verb, optionally clarified with the **COS** comparison‑specification affix.
- In project shorthand:
  - `LVL₁:SUR` = relative *surpassive* (“more … than …”).
  - `COS₁/6` = comparison measured by *relevant outcome / bottom‑line result*; `COS₁/1` = measured by *extent/amount*.
  - put the “than Y” term in **CMP** case.


## 2026-01-28 — Proem 0.1.1 (“This word defines so much…”)
- Locked the interpretive move: “defines so much” → *central salience/constitutive importance* within the discourse, encoded via `ŠH₁` (importance/salience) rather than literal “to define”.
- Added tracked carriers `S«SO MUCH»`, `S«THE GREAT HUMAN CONVERSATION»`, and `S«THIS WORD (LOVE)»` for later resolution into fully canonical degree + referential strategies.

- Desire/want/hope/wish is canonically `GV` (Stem 1 desire/want; Stem 2 wish/hope; Stem 3 aspiration). We previously used `POT` for “hope”; a later cleanup pass can unify this.

- Added ŇŢ₂ as our pinned “rightness/fittingness/propriety” proxy for *The Right* (replacing an earlier misread of `CB`).
