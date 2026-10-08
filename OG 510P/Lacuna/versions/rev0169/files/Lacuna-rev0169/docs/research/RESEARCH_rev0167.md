# Research — rev0167

## Research question

Can Lacuna’s replicated scenario bundles tell the difference between “this condition produced better play” and “raters could recognize which method produced the transcript” without leaking condition labels before primary ratings are frozen?

## Result in this revision

Operationally, yes. Rev0167 adds a typed post-rating masking stage, bundle-sealed masking custody, and a parent-opened unblind gate for bundle-staged child runs. The result is not an efficacy finding; it is a cleaner measurement surface for one important confound.

## Why this matters for Gwern-style retcon planning

The strongest Lacuna condition may be recognizable: it can have different transcript length, checkpoint cadence, public-history continuity, or artifacts of fresh-narrator compression. If raters prefer or dislike it because they recognize the method, primary ratings alone are ambiguous.

A useful evaluation should therefore ask, after raters finish primary scores but before unblinding:

```text
Which method do you think produced this cell?
How confident are you?
What cues led you there?
Did you recognize a method or only guess?
How familiar are you with the methods?
```

Rev0167 records those answers as first-class artifacts and joins correctness only after unblinding.

## New measurable outcomes

Scenario report v3 and bundle report v3 now support:

- per-cell method guesses;
- non-unknown guess rate;
- correct guess count;
- confidence sums;
- recognized-method counts;
- cue retention;
- confusion by true condition and guessed condition; and
- rater-level export of primary ratings alongside masking evidence.

These measures can falsify a too-simple interpretation of blinded ratings. They do not replace blind ratings or prove causal mediation.

## Experimental implication

A pilot can now report, for each condition, both quality scores and recognizability. Especially useful comparisons include:

- Lacuna fresh-narrator versus prompt-only retcon when raters cannot identify the method;
- same comparison among raters who correctly identify it;
- cue analysis for “checkpoint seam,” “style shift,” “overly tidy foreshadowing,” or “public-history summary texture”; and
- sensitivity analysis excluding high-confidence recognizers.

The kernel should not choose one analysis. It should preserve the evidence needed to run several.

## Immediate next step

Run a small scenario bundle and inspect whether masking cues cluster around genuine protocol artifacts or around superficial transcript differences. Use those findings to improve transcript normalization and rater instructions before increasing sample size.
