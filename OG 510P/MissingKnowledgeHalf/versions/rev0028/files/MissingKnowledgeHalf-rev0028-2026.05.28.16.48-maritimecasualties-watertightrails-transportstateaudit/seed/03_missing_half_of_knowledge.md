# The Missing Half of Knowledge — A Seed Document for Corpus Construction

A briefing for what could be built. Treat each section as a research prompt, not a closed list.

This document covers what is actually **four interrelated corpora**:

- **3A.** Negative results / the file-drawer corpus (studies whose findings were null, weren't replicated, weren't published, or were abandoned)
- **3B.** Failed replications (studies that attempted to reproduce a prior finding and didn't)
- **3C.** Engineering mistakes / catastrophic failures (real-world systems that broke, and why)
- **3D.** Genealogy of ideas (who taught whom, read whom, influenced whom — and the anti-genealogy of who reacted against whom)

These corpora are deeply related. A failed replication *is* a negative result. An engineering disaster *is* a negative result from practice rather than experiment. The genealogy of ideas explains why certain failures recurred and certain successes diffused. The corpus, done well, is **the structured record of how human knowledge gets things wrong, and what changes when it does**.

This is the missing half of the history and philosophy of science. The published canon is the survivorship bias; this corpus is the rest.

---

## 1. The premise

Across science, technology, medicine, and engineering, the **negative space** of knowledge — what didn't work, what failed, what was wrong, what was abandoned, what was tried and forgotten — is:

- mostly unwritten
- mostly never aggregated
- structurally underfunded (no career incentive, no journal home for most of it)
- yet **strictly more useful per turn of attention** than additional positive results in many domains

A patient, long-horizon corpus of negative space across science and engineering would be transformative for:

- young researchers (so they don't repeat dead ends)
- policymakers (so they don't believe overstated effects)
- engineers (so they design with awareness of failure modes)
- educators (so they teach an honest picture of science)
- AI training (so models learn the texture of error, not just success)
- philosophers and historians of science (so the empirical base for HPS is honest)
- the public (so trust in science rests on real epistemics, not propaganda)

---

## 2. Why capitalists will not build this

- Negative results have no commercial value in themselves
- The labor is qualitative, slow, interpretive, and ethically constrained (you're describing other people's failures)
- The audience is dispersed across disciplines
- The most valuable version is open access by definition
- Existing platforms (PubMed, Web of Science, Google Scholar) optimize for citation, which is positive-result-biased
- The closest commercial entrant (the AI search startups) treat the literature as ground truth, which is exactly the wrong mental model
- The closest civic entrants (Retraction Watch, OSF, ClinicalTrials.gov) are funded by philanthropy or government and remain underbuilt

---

# CORPUS 3A — Negative Results / The File-Drawer

## 3A.1 What counts as a negative result

The taxonomy matters. Many "negative results" are actually distinct:

- **Null findings.** A predicted effect was not observed. The instrument worked; the prediction failed.
- **Underpowered nulls.** A study that did not detect an effect but couldn't have. These are not real null findings; they are uninformative studies. The corpus should distinguish.
- **Methodologically failed studies.** The instrument or method did not work as intended. Distinct from null findings about the world.
- **Inconsistent findings.** A study found something different from a prior study; neither necessarily wrong.
- **Studies that found the *opposite*.** Counter-findings, which are stronger than null findings.
- **Studies that found a smaller effect than predicted.** Often more informative than nulls.
- **Studies that found the effect only under different conditions.** Boundary conditions.
- **Studies that found heterogeneity where homogeneity was assumed.**
- **Abandoned studies.** Studies that began but were never finished or never written up. Particularly rich and lost.
- **Failed pilot studies.** The deaths of ideas that never got published proposals.
- **Confidential negative results.** Industry trials never disclosed.
- **Theses with negative findings.** Often the only record.
- **Conference posters with negative findings.** Often unpublished.

The corpus should treat each of these as distinct record types.

## 3A.2 Why the file drawer exists

The structural reasons:

- **Publication bias.** Journals prefer positive findings (well-documented across meta-research).
- **Career incentives.** Tenure committees count papers, not failed experiments.
- **Reviewer behavior.** Reviewers reject null findings ("how can we be sure you would have found anything?").
- **The "decline effect."** Many real findings shrink upon replication; researchers face career risk for publishing the smaller follow-up.
- **Funder incentives.** Funders want success stories for reauthorization.
- **Industry secrecy.** Failed drug trials, failed product tests, failed military programs.
- **National security classification.** Failed weapons programs, failed intelligence operations.
- **Reputational risk.** Researchers protect their own positive findings.
- **The honest cost of writing up failures.** Significant work, no career return.
- **The lab notebook culture.** Most data lives in notebooks (paper or electronic) that never become papers.

The corpus should make these structural causes part of the record. It is not just a collection of failures; it is a structural critique of the knowledge-production system.

## 3A.3 Specific famous null / failed cases worth cataloging in depth

The corpus should treat these as case studies — not just lists, but full histories of what happened and what was learned.

### Physics and astronomy

- **Cold fusion (Fleischmann–Pons, 1989)** — the failure of replication, the ongoing low-energy nuclear reaction subculture, what was actually demonstrated and what wasn't.
- **OPERA superluminal neutrinos (2011)** — measurement error, faulty fiber connector; a textbook case of careful announcement and careful retraction.
- **BICEP2 primordial gravitational waves (2014)** — galactic dust, not the early universe; case study in confirmation pressure.
- **The pioneer anomaly** — eventually resolved by thermal modeling.
- **The lithium problem** — primordial nucleosynthesis still hasn't fully resolved.
- **The Hubble tension** — open, but the history of dismissed early measurements is instructive.
- **The Allais effect** — claimed pendulum anomaly during eclipses; not replicable.
- **Variable speed of light proposals** — abandoned.
- **Modified Newtonian Dynamics (MOND)** — ongoing, but the history of dismissal and partial revival is rich.
- **The "fifth force" claims of the 1980s.**
- **The "Allais paradox" decision-theory claims** (different from the eclipse one).
- **Pons and Fleischmann's contemporary failed nuclear claims.**
- **Wandering decimal point in the spinach iron content myth** (different field; instructive).
- **The "faces on Mars" geology debate.**

### Chemistry and materials

- **Polywater (1960s–70s)** — Russian-discovered, hugely consequential null.
- **N-rays (1903, Blondlot)** — classic case of researcher self-deception.
- **The honeycomb / kagome carbons that didn't pan out.**
- **Most claimed room-temperature superconductors before LK-99** — and LK-99 itself (2023).
- **Cold-cathode "Mills BlackLight Power" and hydrino claims.**
- **The Schön scandal (Bell Labs, 2002)** — fabrication, but related to negative-result handling.

### Biology and medicine

- **Cancer biology reproducibility (Reproducibility Project: Cancer Biology)** — most landmark findings did not fully replicate.
- **Candidate-gene era in psychiatric genetics** (~2000–2015) — almost the entire literature did not replicate when GWAS arrived.
- **The "warrior gene" MAOA narrative.**
- **The serotonin theory of depression** — recent meta-analyses suggest weak support; the field's overstatement is a case study.
- **Selenium and prostate cancer (SELECT trial)** — large null after enthusiastic observational data.
- **Vitamin E and heart disease.**
- **Beta-carotene and cancer prevention (CARET, ATBC)** — *increased* lung cancer in smokers.
- **Hormone replacement therapy (WHI 2002)** — large null/harm after observational enthusiasm; case study in observational vs. RCT.
- **Bone marrow transplant for breast cancer** (1980s–90s) — devastating null after widespread adoption.
- **Stem cell hype cycles.**
- **Most Alzheimer's drug trials** — aducanumab, bapineuzumab, solanezumab, semagacestat, tarenflurbil; the amyloid hypothesis's track record is its own subcorpus.
- **The Mediterranean diet PREDIMED retraction and republication.**
- **The "Mozart effect."**
- **The "broken windows" criminological literature** — partial replications, contested.
- **Most fMRI findings in social neuroscience pre-2014** — see "voodoo correlations."
- **Bennett's salmon fMRI** — finding "brain activity" in a dead salmon, a critique not a finding.
- **The "facial feedback" literature on Botox and emotion.**
- **The "marshmallow test"** — Watts et al. 2018 partial failure to replicate.
- **Ego depletion.**
- **Power posing (Carney–Cuddy–Yap)** — Carney later disavowed.
- **Stereotype threat** — partial replications, contested magnitude.
- **Implicit Association Test as a predictor of behavior** — heavily contested.
- **"Grit"** — partial replications.
- **Growth mindset** — partial replications, contested.
- **Babies' moral preferences (Hamlin et al.)** — failed replications.
- **The "Bem ESP" studies** — failed replications, but instructive for what they exposed about statistics.
- **Most priming effects from the 1990s–2000s.**
- **"Embodied cognition"** — mixed picture.
- **The chocolate-improves-cognition literature.**
- **Most candidate findings on the genetics of homosexuality, intelligence, criminality.**

### Social science and economics

- **The Reinhart–Rogoff debt-and-growth finding** — Excel error famous, but the broader claim has not held up.
- **The "voting in elevators" priming studies.**
- **Most "nudge" interventions in large field trials** — meta-analyses show much smaller effects than original studies.
- **Many "happiness" findings.**
- **The Stanford Prison Experiment** — methodological problems, contested status.
- **The Milgram obedience experiments** — partial replications, contested.
- **Many "implicit bias" intervention studies.**
- **Most field experiments on door-to-door canvassing changing opinions** — the LaCour fraud, then the Broockman–Kalla legitimate replication.
- **Economic development RCTs that didn't hold up at scale.**
- **The "10,000-hour rule"** — meta-analyses show much weaker support.

### Drug discovery

- The pharma file drawer is enormous. Per industry estimates, ~90% of candidates entering Phase I do not reach approval. The corpus should treat each Phase failure as a record:
  - Phase I tolerability failures
  - Phase II efficacy failures
  - Phase III pivotal failures
  - Post-market withdrawals (Vioxx, Avandia, rofecoxib, troglitazone, etc.)
- Specific drug-class graveyards:
  - Alzheimer's anti-amyloid (decades of failures)
  - Anti-obesity drugs pre-GLP-1
  - Anti-inflammatory drugs that failed cardiovascular safety
  - Failed sepsis interventions
  - Failed cancer vaccines (pre-modern era)
  - Cardioprotective drugs that didn't help (most antiarrhythmics post-CAST trial)
  - Anti-HIV vaccine attempts
  - Anti-malaria vaccine failures pre-RTS,S

### Computer science / AI

- **The "AI winter" failures.** Expert systems' decline. The Lighthill report on AI (1973).
- **The MYCIN-era promises.**
- **Cyc** — the longstanding project's mixed record.
- **The "Fifth Generation" Japanese AI project.**
- **The decade of failed Bayesian-network medical diagnosis systems.**
- **Failed deep learning attempts pre-2012 backprop scale-up.**
- **Neural Turing Machines and Memory Networks** — direction abandoned.
- **The "Loebner Prize" Turing Test pursuits.**
- **Failed cryptocurrency consensus protocols** (~hundreds).
- **Most blockchain enterprise pilots** (~99% per Gartner).
- **Failed natural language understanding products** in the chatbot waves of 2015–2018.

### Mathematics

In math, a "negative result" is often a proof of impossibility, which is a positive contribution. But there's also:

- **Wrong proofs that were accepted for years.**
- **Refuted conjectures.**
- **Computer-aided proofs whose verification revealed gaps.**
- **Programs of research that turned out to be misdirected.**
- **The "Italian school of algebraic geometry"** — celebrated, later largely re-done after gaps found.

## 3A.4 Sources

### Active platforms

- **F1000Research** — publishes negative results.
- **PLOS ONE** — was meant to publish all sound work; reality has been positive-biased.
- **PeerJ.**
- **Journal of Negative Results in BioMedicine** (defunct, but archived).
- **Journal of Articles in Support of the Null Hypothesis (JASNH).**
- **All Results Journals.**
- **Journal of Pharmaceutical Negative Results.**
- **New Negatives in Plant Science.**
- **The "Journal of Errology"** (various efforts).
- **ScienceMatters** (positive results in small units, but adjacent).

### Preregistration platforms

- **OSF (Open Science Framework).**
- **AsPredicted.**
- **EGAP (Evidence in Governance and Politics).**
- **AEA RCT Registry.**
- **ClinicalTrials.gov** — mandates registration, partial mandate to report results.
- **EU Clinical Trials Register.**
- **WHO ICTRP.**
- **ISRCTN.**

### Replication initiatives

- **Open Science Collaboration (Psychology) 2015.**
- **Many Labs 1, 2, 3, 4, 5.**
- **Reproducibility Project: Cancer Biology.**
- **SCORE program (DARPA).**
- **Replication Markets.**
- **Brian Nosek's broader work at Center for Open Science.**
- **The "Reproducibility Crisis" surveys (Nature 2016, others).**

### Retraction Watch

- **The Retraction Watch Database.** Not just negative; also fraud, but rich.
- Pubpeer (open peer review and post-publication critique).

### Theses

- **ProQuest Dissertations.**
- **National library theses collections** (UK EThOS, etc.).
- Most contain a chapter of "things we tried that didn't work."

### Notebooks and informal sources

- Lab notebooks (rarely public; some scientists are starting open notebooks).
- Github repositories with abandoned branches.
- Slack/Discord/email threads (private but rich).
- Blog posts (often the only record).
- Twitter/Bluesky threads (often the only record).
- Conference talks not turned into papers (slides sometimes archived).

### Adjacent literature

- **Meta-research / metascience.** John Ioannidis, Brian Nosek, Daniel Kahneman, Andrew Gelman, Uri Simonsohn, Joe Simmons, Leif Nelson.
- **Statistics critique literature.** Cohen, Meehl, Gigerenzer, Cumming.
- **The "Garden of Forking Paths"** literature.
- **The p-hacking, HARKing, garden of forking paths, optional stopping literatures.**
- **History of medicine on overpromising:** *Ending Medical Reversal* by Prasad & Cifu; *Snake Oil Science* by Bausell.

## 3A.5 What the record should contain

A negative-result record might have:

- **Identifier** (DOI, preprint ID, registration ID, internal ID)
- **Authors** (with affiliations at time of work)
- **Hypothesis** (the specific prediction tested)
- **Pre-registration** (if any; with link)
- **Method** (briefly; with link to full method)
- **Population / sample / dataset**
- **Power analysis** (was the study capable of detecting the predicted effect?)
- **Statistical methods**
- **Result** (with effect size, confidence interval, p-value — but emphasized as point estimates with uncertainty)
- **Authors' interpretation**
- **Subsequent fate** — was this published? cited? followed up?
- **Replication attempts** (linked to records)
- **Field's response** — did the literature update?
- **Why authors think it failed/was null** (their own theory)
- **Cross-references** — what positive findings does this contradict or qualify?
- **Cross-references to engineering practice** — if this finding informed real-world practice, was practice updated?

The corpus's distinctive contribution is **linking** — every negative result should connect to the positive results it qualifies, the replications it supports, and the practical consequences (if any).

## 3A.6 Edge cases

- **Negative results that became famous positives later.** Continental drift. Helicobacter pylori. Some autoimmune theories. The corpus must distinguish "currently negative" from "permanently negative" — and respect that "permanent" is rare.
- **Negative results that should never have been positive.** Phrenology, lobotomy outcomes, eugenic predictions. The corpus is a tool for getting these out of the literature.
- **Negative results in contested moral domains.** IQ and group differences, gender and cognition, sexual orientation and biology. The corpus must be especially careful with both the social context and the epistemics.
- **Negative results that were politically suppressed.** Tobacco research, climate research, lead research, pharmaceutical safety. These overlap with the engineering-failures corpus.
- **Negative results that were *false* negatives.** Underpowered studies, bad measurements. The corpus should not enshrine these as null.
- **Negative results in domains with no replication culture.** Anthropology, history, qualitative sociology. These have different epistemics; the corpus should respect them.
- **Negative results in fields that don't use that language.** Mathematics ("counterexample"), law ("losing argument"), philosophy ("refutation"). The corpus should be cross-disciplinary in vocabulary.

---

# CORPUS 3B — Failed Replications

This is a subspecies of 3A but worth distinguishing because the **structure** of the record is different.

## 3B.1 The structure of a replication-failure record

- **Original study** (full citation, claim, effect size, sample, method).
- **Replication attempt** (citation, sample, method).
- **Was it pre-registered?**
- **Was it a direct or conceptual replication?**
- **Result** (effect size, confidence interval).
- **Comparison** — magnitude of replication effect vs. original.
- **Original authors' response** (with link).
- **Replicators' response to the response.**
- **Subsequent attempts** — what did other replications find?
- **Meta-analytic synthesis** (linked).
- **Field's status** — does the textbook still say it? Does the consensus still hold it?

## 3B.2 The categories

- **Direct replication.** Same procedure, same population type.
- **Conceptual replication.** Different procedure, same construct.
- **Meta-analytic disconfirmation.** Aggregating across studies reveals effect is much smaller or absent.
- **Adversarial collaboration.** Original authors and skeptics design joint study.
- **Mega-study.** Large multi-site pre-registered effort.
- **Many Labs style.** Multiple independent labs running the same protocol.
- **Reanalysis disconfirmation.** Same data, different analysis, different conclusion.
- **Forensic disconfirmation.** Examination of original data reveals statistical irregularities (Simonsohn, Heathers, others).

## 3B.3 Patterns in failed replications

Worth surfacing in the corpus:

- Original studies with small samples
- Original studies with multiple analytic paths
- Original studies in psychology pre-2015 (the inflection point)
- Studies with conflicts of interest
- Studies with surprising headline effects
- Studies in fields with strong narrative pressure
- Studies relying on subjective measurement
- Studies with high subject heterogeneity

The corpus should make patterns visible without making them deterministic.

## 3B.4 The replication ecosystem

- **Curate Science.** (Tilburg) — replication metadata.
- **Replication Database (Forsch, etc.).**
- **The Reproducibility Project: Psychology — its data archive.**
- **The Many Labs projects — their data archives.**
- **Loken & Gelman, "Measurement error and the replication crisis."**
- **The Open Science Foundation broader ecosystem.**

## 3B.5 Specific patterns the corpus should make findable

- **Pre-registration adoption timing.** When did each field adopt pre-registration? Has it changed replication rates?
- **Open data and code requirements.** When did journals adopt them, and what happened to replication rates?
- **The "decline effect."** Effects shrink over time across many fields. The corpus should make this empirically observable.

---

# CORPUS 3C — Engineering Mistakes and Catastrophic Failures

## 3C.1 The premise

Failures of engineered systems are usually documented by accident investigators after the fact. The documentation is scattered across NTSB, NASA, the Chemical Safety Board, the CSB animations (extraordinary public-good output), military investigation reports, civil court cases, corporate reports, academic case studies, and journalism. The corpus should aggregate, normalize, and tag.

## 3C.2 The categories

### Civil engineering

- **Bridge failures**
- **Building collapses**
- **Dam failures**
- **Tunnel collapses**
- **Foundation failures**
- **Earthquake-induced failures**
- **Wind-induced failures**
- **Construction failures**
- **Cofferdam failures**

### Aerospace

- **Commercial aviation accidents** — extraordinarily well-documented; NTSB and ICAO are the canonical sources
- **General aviation accidents**
- **Military aviation accidents** (less public)
- **Spaceflight failures** — Apollo 1, Challenger, Columbia, recent SpaceX, Soyuz, Long March
- **Launch failures** — extensive history
- **Satellite failures** — Hubble's initial optics, ExoMars, etc.

### Nuclear

- **Three Mile Island**
- **Chernobyl**
- **Fukushima**
- **SL-1**
- **Mayak / Kyshtym**
- **Tokaimura**
- **The criticality accidents corpus (Slotin, Daghlian, others)** — small but instructive
- **Submarine reactor incidents (Thresher, Scorpion, K-19, K-27, K-219, K-141 Kursk)**

### Marine

- **Titanic** (still the case study)
- **Estonia**
- **Sewol**
- **Costa Concordia**
- **Wakashio**
- **Exxon Valdez**
- **Deepwater Horizon**
- **Andrea Doria**
- **Edmund Fitzgerald**
- **MOL Comfort**
- **Container ship structural failures (the MV Napoli, others)**
- **Liberty ship welding failures (WWII)**

### Chemical and industrial

- **Bhopal**
- **Texas City BP refinery**
- **West, Texas fertilizer plant**
- **Flixborough**
- **Seveso**
- **Toulouse AZF**
- **Tianjin port**
- **Beirut port (2020)**
- **Phillips 66 Pasadena**
- **Bayer CropScience Institute, WV**
- **DPC Enterprises**
- **The full Chemical Safety Board (CSB) report archive**

### Mining

- **Aberfan**
- **Mount Polley**
- **Brumadinho** (and Mariana, Brazil)
- **Buffalo Creek**
- **Centralia**
- **Upper Big Branch**
- **Pike River**
- **Soma**

### Energy

- **Banqiao Dam (1975)** — one of the worst engineering disasters in history; underdocumented in English
- **St. Francis Dam**
- **Vajont**
- **Teton Dam**
- **Malpasset**
- **Oroville spillway near-failure**

### Medical devices and pharmaceutical manufacturing

- **Therac-25** (race condition causing radiation overdose; canonical software-engineering case)
- **Heart valve failures (Bjork-Shiley convexo-concave)**
- **Hip implant failures (DePuy ASR)**
- **Mesh implant failures**
- **Insulin pump failures**
- **Pacemaker recalls**
- **Failure modes in compounding pharmacies (NECC meningitis outbreak, 2012)**

### Software and IT

- **Therac-25** (cross-listed)
- **Knight Capital ($440M in 45 minutes, 2012)**
- **Ariane 5 Flight 501 (1996)**
- **Mars Climate Orbiter (1999)**
- **Mars Polar Lander (1999)**
- **Patriot missile clock drift in Dhahran (1991)**
- **AT&T long distance crash (1990)**
- **Northeast blackout (2003) — alarm system race condition**
- **The Y2K problem (averted disaster as data)**
- **Heartbleed (2014)**
- **Equifax breach (2017)**
- **The CrowdStrike–Microsoft outage (2024)**
- **Boeing 737 MAX MCAS (software-driven engineering failure)**
- **The UK Post Office Horizon scandal** (software defects + institutional failure = worst miscarriage of justice in UK history)
- **Toyota unintended acceleration**
- **The Dieselgate emissions software**

### Transportation systems

- **All major aircraft accidents** (NTSB, ICAO, AAIB archives)
- **Rail accidents** (Lac-Mégantic, Eschede, Amagasaki, Granville, Hatfield)
- **Highway design failures** (specific intersections, bridges)
- **Pipeline failures** (Carlsbad, Bellingham, San Bruno, Mariner East)

### Adjacent: financial and policy failures as engineering

- The financial system as an engineered system has its own failure corpus (LTCM, 2008, Knight Capital, Flash Crash 2010)

## 3C.3 Why this corpus is so rich

Engineering failure documentation is **the most mature subgenre** of the "negative results" universe. The professions that engineer high-risk systems (aviation, nuclear, chemical, civil) have built genuinely impressive accident-investigation institutions over the last century:

- **NTSB** (US transportation)
- **AAIB** (UK air accidents)
- **BEA** (France)
- **JTSB** (Japan)
- **TSB** (Canada)
- **ATSB** (Australia)
- **CSB** (US chemical)
- **NRC** (US nuclear)
- **IAEA** (international nuclear)
- **NIST disaster investigations** (e.g., World Trade Center collapse)

These produce **structured, primary-source, public-domain documents**. The corpus's job is largely aggregation and normalization, not original research.

## 3C.4 What "done well" looks like for engineering failures

Each incident record should have:

- **Incident** (name, date, location, fatalities/injuries/cost)
- **System** (what was the engineered object)
- **Operators / owners** (organizations involved)
- **Designers / builders / manufacturers** (organizations involved)
- **Regulators** (responsible bodies)
- **Sequence of events** (timeline, in detail)
- **Proximate cause** (the immediate failure)
- **Contributing factors** (the chain)
- **Root causes** (organizational, cultural, regulatory)
- **Latent conditions** (the slow conditions that allowed it)
- **Decisions that mattered** (good and bad, at each level)
- **Counterfactuals** (what would have prevented this)
- **Investigation report** (linked, with full text where possible)
- **Lessons codified** (recommendations from investigators)
- **Subsequent regulatory action** (linked)
- **Subsequent design changes** (linked)
- **Lessons *not* learned** (when has the same failure pattern recurred?)
- **Cross-references** to similar failures
- **Industry response** (corporate communications, public statements)
- **Legal proceedings**
- **Personal accounts** (witnesses, survivors, families)

## 3C.5 Theories of failure to include

The corpus should be theoretically grounded in:

- **Charles Perrow, *Normal Accidents***
- **James Reason, "Swiss cheese" model**
- **Diane Vaughan, *The Challenger Launch Decision* — "normalization of deviance"**
- **Sidney Dekker, *The Field Guide to Understanding 'Human Error'***
- **Erik Hollnagel, resilience engineering and Safety-II**
- **Karl Weick on sensemaking**
- **Nancy Leveson, system safety, *Engineering a Safer World***
- **Henry Petroski's whole body of work**
- **Don Norman, *The Design of Everyday Things***
- **Atul Gawande on medical error**
- **Lucian Leape on patient safety**
- **The high-reliability organizations literature (Roberts, Rochlin, La Porte)**
- **Sidney Dekker on "just culture"**
- **The *Field Guide to Understanding Aerospace Mishaps* tradition**

The corpus is the empirical base these theorists work from. It should be cross-tagged with their concepts.

## 3C.6 The "recurring patterns" cross-corpus

What the corpus enables that nothing else does: **noticing recurrence**.

- The "two-man rule" failures across industries
- The interface ambiguity failures (Mars Climate Orbiter, Air Canada Gimli Glider, others — units mismatches)
- The "experienced operator overrides safety system" failures (Chernobyl, Three Mile Island)
- The "boss in the cockpit / boss in the meeting" failures (deference to authority)
- The "production pressure overrides safety" failures (Challenger, BP Texas City)
- The "missing redundancy" failures
- The "redundancy that wasn't really redundant" failures (common-mode)
- The "alarm fatigue" failures (Three Mile Island, AT&T 1990)
- The "training out of date" failures
- The "documentation lied" failures
- The "warning was given, ignored" failures
- The "warning was given, not understood" failures
- The "warning was suppressed" failures
- The "regulatory capture" failures
- The "whistleblower silenced" failures
- The "near-miss not investigated" failures
- The "test conditions did not match field conditions" failures

The corpus should be queryable by pattern across industries.

## 3C.7 Specific things ChatGPT (or any builder) might miss

- **The Chemical Safety Board's animations are extraordinary.** A 10-minute CSB animation often communicates more than a 200-page report. The corpus should reference them as primary sources.
- **The Aviation Safety Reporting System (ASRS)** — pilots can self-report near-misses anonymously. Huge underused corpus.
- **The MARS reporting system** — NASA's analogous space-flight reporting.
- **CIRAS, CHIRP** — confidential reporting in UK rail and aviation.
- **The NRC Operating Experience reports.**
- **Pipeline and Hazardous Materials Safety Administration (PHMSA) failures database.**
- **The MAIB monthly digest** is a goldmine of small marine incidents.
- **The Air Accident Investigation reports of small countries** (often in English) sometimes contain unique lessons.
- **The "Lessons Learned Information System" of NASA** is a model that should be more widely emulated.
- **DARPA's "AI Next" failure write-ups** (some are public).
- **The IT industry's lack of equivalent**. Software engineering does not have a CSB or NTSB. This is a meta-finding the corpus should make visible.
- **The military industrial failure corpus.** Mostly classified, but the unclassified portion (B-1 issues, V-22 Osprey, F-35, Zumwalt, LCS) is rich.
- **The Soviet / Russian failure corpus** (Buran, Energia, K-class submarines, Kursk, Mars probe failures) — underdocumented in English.
- **The Chinese failure corpus** — even less documented in English.
- **The "dark patterns" in software design** as a kind of intentional engineering failure (toward users, in favor of operators).

## 3C.8 The "near-miss" subcorpus

Near-misses are where most learning happens but where most documentation is private. The corpus should treat near-miss reporting as a distinct subcorpus, and study the systems that successfully collect it (aviation ASRS as the model).

## 3C.9 Ethical principles

- **No survivor's trauma weaponized for content.**
- **Family wishes about identifying their loved ones.**
- **The dignity of the dead.**
- **The complexity of fault.** Most failures are systemic; the corpus should not become a witch hunt of individual operators.
- **The "blame culture" critique.** Sidney Dekker's work on just culture is essential framing.
- **The hindsight bias warning.** Every record should note: at the time, the decision looked different.

---

# CORPUS 3D — Genealogy of Ideas

## 3D.1 The premise

Ideas don't appear from nowhere. They come from teachers, books, conversations, conferences, archives. The genealogy of ideas — who taught whom, who read whom, who reacted against whom, who was friends with whom — is **the social structure of intellectual history**.

This corpus is the most interpretive of the four, because attributing influence is inherently interpretive. But there are well-established methods.

## 3D.2 Existing infrastructure (good starting points)

- **The Mathematics Genealogy Project (NDSU)** — advisor/student relationships in mathematics. The gold standard for any single field. ~300,000+ records.
- **Academic Tree (academictree.org)** — has subdomains: NeuroTree, PsychTree, ChemTree, PhysicsTree, AnthropologyTree, etc. Less comprehensive than math, but the model is right.
- **Wikipedia's "Doctoral advisor / Doctoral students" infoboxes** — partial but useful.
- **OpenCitations / OpenAlex / CrossRef** — citation networks at scale.
- **Inspire-HEP** — high-energy physics literature.
- **arXiv** — author networks.
- **Zentralblatt and MathSciNet** — math literature.

## 3D.3 Dimensions of genealogy

- **Doctoral advisor → student** (the most formal)
- **Postdoc advisor → postdoc**
- **Habilitation / Privatdozent traditions** (Continental Europe)
- **Master → apprentice in non-academic fields** (e.g., music composition lineages, craft lineages)
- **Influence as cited** (citation networks)
- **Influence as self-declared** (acknowledgments, dedications, prefaces, interviews)
- **Influence as observed by historians** (the most interpretive)
- **Coauthorship networks** (Erdős numbers as the canonical case)
- **Conference attendance / seminar attendance**
- **Visiting fellowships** (e.g., Institute for Advanced Study visits)
- **Correspondence networks** (the Republic of Letters)
- **Reading lists** (what was on whose syllabus)
- **Marginalia** (what philosophers wrote in their copies of other philosophers)
- **Translation chains** (who introduced whose work to which language)
- **Reception** (how was the work received, by whom, when)

## 3D.4 Anti-genealogy

The corpus should also capture **reactions against**. Often more telling than positive influence:

- The Frankfurt School against positivism
- Wittgenstein's later work against his earlier
- Continental vs. analytic philosophy
- Symbolic vs. connectionist AI
- Pre-WWII vs. post-WWII economics
- Behaviorism vs. cognitivism in psychology
- The Bourbaki reaction against geometric intuition
- Heterodox vs. orthodox economics
- Modernist vs. postmodernist architecture
- The various reactions against Freud, Marx, Foucault

## 3D.5 Specific traditions / scenes worth mapping in depth

These are intellectual scenes where the genealogy is dense, partially documented, and culturally important.

### Physics and natural science

- **Copenhagen Group (Bohr-centered)**
- **Göttingen mathematics-physics (Hilbert-Born-Heisenberg)**
- **Cambridge (Maxwell-Thompson-Rutherford-Dirac)**
- **Princeton IAS (Einstein-Gödel-Oppenheimer)**
- **Manhattan Project network**
- **Los Alamos and Livermore alumni**
- **Bell Labs (Shannon-Pierce-Shockley network)**
- **The Cavendish Laboratory lineage**
- **The Solvay Conferences** (each one a snapshot of physics genealogy)
- **The Pugwash Conferences** (post-war science and policy)
- **The Macy Conferences (cybernetics, 1946–1953)**
- **The Dartmouth Workshop 1956 (founding of AI)**
- **Asilomar conferences (recombinant DNA 1975; AI safety, repeated)**

### Mathematics

- **Bourbaki**
- **The Cantor → Hilbert → Gödel → Cohen chain in set theory**
- **The Princeton number theory tradition**
- **The Russian school (Kolmogorov, Gelfand, Manin)**
- **The Hungarian school (Erdős, Rényi, Lovász)**
- **The Indian mathematical tradition (Ramanujan and Tata Institute)**
- **The French Bourbaki and successor scenes**

### Computing and AI

- **MIT AI Lab (Minsky, Papert, McCarthy origins)**
- **Stanford AI Lab (McCarthy, Feigenbaum)**
- **Carnegie Mellon (Simon, Newell)**
- **Xerox PARC**
- **Bell Labs computing**
- **Berkeley (BSD, Unix)**
- **The connectionist lineage (Rosenblatt, Rumelhart, Hinton, LeCun, Bengio)**
- **The symbolic lineage**
- **The Bayesian lineage (Jaynes, Pearl, Jordan, Murphy)**
- **The reinforcement learning lineage (Sutton, Barto, Bertsekas)**
- **The deep learning lineage post-2006**
- **The current AI safety scene (MIRI/CHAI/Anthropic/DeepMind lineages)**

### Philosophy

- **The Vienna Circle**
- **The Frankfurt School**
- **The Oxford ordinary language tradition (Austin, Ryle, Strawson)**
- **The Cambridge tradition (Russell, Moore, Wittgenstein, Anscombe)**
- **The Pittsburgh school (Sellars, McDowell, Brandom)**
- **Continental philosophy lineages (Husserl → Heidegger → Sartre / Merleau-Ponty / Levinas)**
- **Post-structuralism (Foucault → Deleuze → Derrida)**
- **American pragmatism (Peirce → James → Dewey → Rorty)**
- **The Kyoto School**

### Economics

- **The Austrian School**
- **The Chicago School (Friedman, Becker, Lucas)**
- **The Cambridge UK / Cambridge US debate**
- **The MIT-Stanford lineage (Samuelson → Solow → Stiglitz, etc.)**
- **The behavioral economics lineage (Kahneman, Thaler)**
- **The development economics lineage (Sen, Banerjee, Duflo, Kremer)**
- **The heterodox lineages (Post-Keynesian, MMT, ecological economics)**

### Literature and arts

- **The Bloomsbury Group**
- **The Inklings (Lewis, Tolkien, Williams)**
- **Black Mountain College**
- **The Beats**
- **The New York School**
- **The Beat poets**
- **Black Arts Movement**
- **The Iowa Writers' Workshop network**
- **MFA program lineages**

### Architecture

- **The Bauhaus diaspora**
- **The Harvard GSD (post-Gropius)**
- **The "New York Five"**
- **The Texas Rangers (Hejduk, Hoesli, Slutzky, Rowe)**
- **The Yale lineage**
- **The IIT Mies tradition**

### Science scenes that crossed disciplines

- **Santa Fe Institute (complexity)**
- **The Hutchins Center at the Center for Advanced Study in the Behavioral Sciences**
- **The Tavistock Institute (group dynamics)**
- **Esalen**
- **The Bell Labs computing+linguistics cross-pollination**

## 3D.6 What records in the genealogy corpus look like

- **Person record** (canonical name, dates, affiliations over time)
- **Influence record** (person → person; with type: advisor / postdoc / collaborator / acknowledged influence / reacted against / corresponded with)
- **Work record** (a paper, book, talk, manuscript, with cited works, cited-by works)
- **Scene record** (an institution, group, or moment with members and dates)
- **Event record** (a conference, seminar, summer school with attendees)

The corpus should make queryable:

- "Who are all the descendants of [X]?"
- "Who were the most influential mentors in [field, period]?"
- "Who taught [unexpected pair] — and did they know each other?"
- "Who was at the conference where [famous result] was first announced?"
- "Whose students became more influential than them?"
- "Who never had students but had enormous influence through writing?"

## 3D.7 The lost lineages

The corpus should especially preserve:

- **Women who were students of famous men, often unacknowledged.** Their lineages are particularly endangered.
- **Black, Brown, Indigenous, and other underrepresented intellectual lineages.** The "great man" model erases them.
- **Non-Western lineages.** The Indian, Chinese, Japanese, Iranian, Egyptian, Latin American, African intellectual lineages.
- **The intellectual labor of translators, editors, conference organizers, secretaries.**
- **The "second-tier" scholars who taught the famous ones.** Often more important than visible.
- **Oral teaching traditions.** Many fields have key teachers who barely published.
- **The samizdat and underground traditions.** Soviet, Iranian, Chinese, others. Ideas circulated outside formal channels.

## 3D.8 Specific things ChatGPT (or any builder) might miss

- **The dedications and prefaces of academic books.** These are dense influence-tracking material, rarely systematically extracted.
- **The acknowledgments sections of papers.** Less formal than citations, often more revealing.
- **Conference attendance lists.** Often only in archives.
- **Festschrifts** (books honoring teachers) — direct testaments of lineage.
- **Memorial issues of journals** — same.
- **Obituaries written by former students.**
- **Memoirs and autobiographies** — usually with chapters about influences.
- **Oral history interviews** (American Institute of Physics, Computer History Museum, Smithsonian, Caltech Archives, etc. all have collections).
- **Correspondence archives** (Library of Congress, Harvard, Yale, Princeton, etc. all have manuscript archives).
- **The Republic of Letters digital project (Stanford).**
- **The Darwin Correspondence Project, the Einstein Papers Project, etc.** — single-person corpora as models.

---

# THE UNIFIED CORPUS

## 4. Why the four corpora belong together

The four corpora interlock:

- **Negative results and engineering failures are the same phenomenon at different scales.** A failed clinical trial and a bridge collapse are both empirical disconfirmation. The corpus should treat them with the same dignity.
- **Failed replications and engineering failures both reveal what wasn't known.** They are diagnostic.
- **The genealogy of ideas explains why some failures recurred and some did not.** The lineage of safety thinking matters to which industries learned which lessons. The lineage of psychological theories matters to which "findings" persisted into the textbook canon. The lineage of economic schools matters to which policy disasters were predicted.
- **Together they form an empirical history of how knowledge actually progresses.** Not the heroic story; the actual story.

## 5. Schema for the unified corpus

The minimum joint record might have:

- **Type** (negative result / failed replication / engineering failure / influence-link / lost-lineage entry)
- **Domain** (field, subfield, application area)
- **Subjects** (people, institutions, systems involved)
- **Time** (when did this happen; when was it documented)
- **Place** (where was the research, system, event)
- **Sources** (primary, with permanence — DOIs, archives, official reports)
- **Claim** (what is being asserted)
- **Status** (uncontested / contested / superseded)
- **Cross-references** (positive findings this qualifies, related failures, related lineage)
- **Lessons / consequences** (what changed, what didn't)
- **Why-not-known** (why isn't this widely known?)

## 6. The audience and uses

Done well, this corpus would be used by:

- **Graduate students starting projects** — to learn what's been tried.
- **Replication researchers** — to identify the most-cited fragile findings.
- **Engineers** — to learn from history before designing.
- **Educators** — to teach the actual history of science, not the heroic version.
- **Policy makers** — to weight scientific claims appropriately.
- **Journalists** — to fact-check claims of consensus.
- **AI training** — to ground models in epistemic humility.
- **Historians of science** — as primary infrastructure.
- **Philosophers of science** — as empirical base.
- **Foundations and funders** — to identify under-funded replication and meta-research.

## 7. Adjacent corpora the project enables

- **The "decline effect" cross-domain corpus.** Tracking effect sizes over time across fields.
- **The "predictions that failed" corpus.** Specifically future-prediction failures (Erlich's *Population Bomb*, Y2K, peak oil 1970s, AI timelines, etc.).
- **The "consensus that wasn't" corpus.** Historical moments of apparent consensus that proved wrong.
- **The "isolated dissenters who were right" corpus.** Harder; survivorship-biased. But Semmelweis, McClintock, Marshall and Warren, others. Must be handled carefully — for every right dissenter there are thousands who were just wrong.
- **The "retrospective debunking" corpus.** When was [folk wisdom / textbook claim] first contested and when did it die in the literature.

## 8. What ChatGPT (or any builder) is most likely to under-engineer

- **The provenance and permanence of links.** Most sources rot. The corpus must capture, archive, and re-host as ethically and legally appropriate (Internet Archive partnerships matter).
- **The cross-disciplinary translation.** Vocabulary varies. The corpus must include domain-vocabulary mappings.
- **The graceful handling of contested status.** "This is null" / "this is debated" / "this is currently revived" — the corpus must track epistemic status over time.
- **The handling of authors' wishes.** Many researchers do not want their failed studies indexed prominently. Ethical defaults matter.
- **The handling of cumulative learning.** A null result followed by ten replications followed by a confirmed positive is a different beast from a one-off null. The corpus's job is the long view.
- **The relationship between literature and practice.** A finding can die in the literature and persist in practice for decades. The corpus should track both.

## 9. Tone and ethic

The corpus is not a museum of mistakes. It is not a wall of shame. It is the **honest record of how knowledge actually advances**, which is mostly through failure, correction, and rare consolidation. It is built in the spirit of:

- Karl Popper (falsification as the engine of science)
- John Ioannidis (most findings are likely false)
- Daniel Kahneman (we are predictably wrong)
- Henry Petroski (engineering progresses by failure)
- Diane Vaughan (organizations normalize deviance)
- Imre Lakatos (research programs, not theories, are the units)
- Thomas Kuhn (paradigms, anomalies, crises, shifts)
- Charles Sanders Peirce (fallibilism as the proper epistemic stance)

The corpus is a tool for collective epistemic maturation. It is unglamorous, slow, expensive work that returns disproportionate value if done patiently.

## 10. A final note

Of the three corpora considered in this set of seed documents — the vocabulary of dying, police misconduct records, and the missing half of knowledge — this one (the missing half) has the broadest constituency and the smallest existing infrastructure. Retraction Watch, the Reproducibility Project, the Mathematics Genealogy Project, the NTSB archive, and so on are extraordinary but uncoordinated. The opportunity is the unification.

The corpus is the dark matter of intellectual history. It outweighs the visible canon, holds the canon in shape, and is mostly invisible. Building it is one of the few projects that, done with the right patience, would change how science thinks about itself.
