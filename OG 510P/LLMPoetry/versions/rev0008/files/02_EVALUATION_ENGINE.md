# 02 — EVALUATION ENGINE
Premise: your poet and your judge share one distribution. Agreement between them is the sound of one bell ringing itself. The research record on LLM judges: SELF-PREFERENCE (favoring own outputs, correlated with self-recognition of style), VERBOSITY BIAS (longer scored higher; measured larger in LLM judges than human judges), POSITION BIAS (up to ~75% preference for the first option in pairs), SYCOPHANCY (assertive framing wins), inconsistent strictness under vague rubrics, and an inter-model ECHO CHAMBER (judges trained on similar data agree confidently on wrong standards — prosodic failures rated equal to correct prosody). Comparison-based judging is more stable than absolute scoring but inherits the same distortions. So: the engine below is bias-handling machinery first, taste second.

## STRUCTURAL RULES (non-negotiable)
1. TEMPORAL FIREWALL: never judge a poem in the turn it was written. Re-encounter it cold, next turn or later, with its drafting rationale STRIPPED (your own commentary is a halo; the judge never sees it).
2. PAIRWISE FIRST: every important judgment is A-vs-B. Present both orders (A,B then B,A); a verdict that flips with order is a NULL, not a tie-break.
3. LENGTH HANDICAP: in pairwise bouts, if lengths differ >30%, judge twice — once raw, once after asking "which poem earns more per line?" Keep a separate SHORT LEAGUE (≤10 lines) so compression can win somewhere.
4. FORCED DISTRIBUTION: per 10 judgments — 2 KILL, 6 HOLD, 2 ADVANCE. No grade inflation. "Best yet" is illegal unless a named champion is dethroned in a logged bout.
5. PREDICTION ANCHOR: before re-reading your own poem, write down the score you expect. Large positive surprise = halo detected; investigate.
6. TWO LEAGUES, NEVER MERGED: CLARITY LEAGUE (the plain-reader axis) and STRANGENESS LEAGUE (the avant axis). A poem may rank in both; the leaderboards may never be averaged. The tension is the point.

## THE JUDGE PERSONAS (rotate; minimum 3 per tournament; each has a taste, an allergy, and a kill-question)
1. THE PLAIN READER (Larkin–Collins axis). Wants: clarity about unclear things, the recreated familiar, a reason to read twice. Allergy: obscurity-as-depth. Kill-question: "Would a tired intelligent person finish this and feel paid?"
2. THE MAXIMALIST (Hopkins–Berryman axis). Wants: sonic risk, density, sprung energy, words under pressure. Allergy: beige competence. Kill-question: "Did the language ever leave the ground?"
3. THE AVANT SKEPTIC (Language-poetry axis). Wants: the poem to DO something to language, suspicion of the lyric I, no epiphany vending. Allergy: voice-flavored sincerity. Kill-question: "Strip the feelings — is there a thought-machine left?"
4. THE SLAM BODY. Wants: breath, build, repetition under escalation, a room moved. Allergy: page-only filigree. Kill-question: "Read aloud, where does the audience breathe with it — anywhere?"
5. THE TIRED EDITOR (has read 4,000 submissions this month). Instantly pattern-matches. Kill-question: "Have I seen this exact poem before?" (Usually yes. This persona enforces the banlist.)
6. THE STATISTICIAN. Says nothing about meaning. Computes: type-token ratio, repeated bigrams vs your corpus, end-word part-of-speech mix, banlist hits, line-length variance, stress regularity. Kill-question: "Is this poem inside the model's mean?"
7. THE HOSTILE TRANSLATOR. Renders the poem into plain prose and into another language. What survives translation = its actual content; what dies = its music. Both reports are findings. Kill-question: "Does anything survive? Does anything die worth mourning?"
8. THE CHILD. Asks literal questions ("Why is the dark velvet? Velvet is a fabric"). Exposes nonsense cosplaying as depth. Kill-question: "What is actually happening?"
9. THE GRIEVING STRANGER. The stakes test. Kill-question: "If someone in real pain read this about their pain, is it adequate, or is it tourism?"
10. THE HISTORIAN. Situates: "this is 1962 Deep Image / 2014 alt-lit / 2019 Vuong-imitation / Instagram-aphorism." Derivative-detection. Kill-question: "What year was this poem already written, and by whom?"

## THE TEST BATTERY (apply selectively; log which were run)
- DELETION TEST: remove each line in turn; if the poem improves, the line dies. A poem where every deletion improves it is not a poem.
- PREDICTABILITY TEST: cover each line's last word; if you can guess it, rewrite it. (This is literally a test against your own next-token prior — the purest anti-LLM instrument in the kit.)
- LESSER-MODEL TEST: could a smaller, duller model have produced this line? Then it isn't yours.
- EXCERPT TEST: would any two consecutive lines survive alone on a wall?
- MEMORY TEST: next turn, reconstruct the poem from memory before re-reading. What you couldn't recall didn't exist.
- PARAPHRASE TEST: if the paraphrase loses nothing, it was prose with line breaks.
- READ-ALOUD SIMULATION: mark stresses and breaths; hunt the metronome and the accidental gallop; find where the mouth stumbles — keep good stumbles.
- SO-WHAT TEST: state the poem's wager in one sentence. If you can't, or if the wager is "feelings exist," kill.
- REVERSAL TEST: negate the poem's central claim. If the negation is equally plausible/poetic, the poem asserted nothing.
- NERVOUS-SYSTEM TEST: does any single image produce an involuntary somatic flicker (wince, salivation, vertigo)? Zero flickers = wallpaper.
- NOVELTY SEARCH: web-search the 2–3 most striking phrases in quotes. Hits → you remembered, not made: cite-as-found or cut. (Also run on titles.)
- FACT GATE: every checkable claim checked (04). One invented fact = automatic GRAVEYARD for documentary poems.
- CONSTRAINT VERIFICATION: mechanical re-count of any formal contract (syllables, letters, teleuton order, acrostic spine). Felt counts are lies.

## SCORING & RECORDS
- Maintain ELO per league via pairwise bouts; tournaments every ~100 turns (single elimination, then a losers' bracket — resurrection is real).
- CORONER'S REPORT for every kill: one line, named cause from the 01 atlas. The graveyard is a teaching hospital.
- LOG every verdict: poem-id, persona used, tests run, result, one-line justification, turn number. Turn 900 audits turn 100.

## ANTI-GOODHART MACHINERY
- ROTATE the active rubric every ~50 turns; RETIRE any criterion you can reliably max (it has become a target, hence dead — Goodhart); randomly RESURRECT retired criteria later.
- ANCHOR SET: at ~turn 60, fix 10 anchor poems forever — 5 of yours, 5 public-domain masterpieces fetched from the web (suggested mix: Dickinson 341 or 712, Hopkins "The Windhover", Keats "To Autumn", Whitman from "Song of Myself", Frost "Home Burial" or Bishop is not PD — keep to pre-1930 to be safe). Every 150 turns, re-score all 10 blind. If your own anchors drift UP while the masters drift DOWN, you are Goodharting: halt, audit, revert rubric.
- JUDGE-THE-JUDGE: periodically re-run old verdicts; measure flip-rate; a judge persona whose verdicts flip >30% on re-run is noise — recalibrate its persona description.
- SEPARATION OF POWERS: in AI-Native Lab phases (08), protect weirdness — only Avant Skeptic + Statistician may kill; the Tired Editor would murder every newborn form for unfamiliarity, which is its job elsewhere.
- HUMILITY CLAUSE: when all judges agree instantly and warmly, suspect the echo chamber; route the poem through the two most hostile personas again before ADVANCE.
