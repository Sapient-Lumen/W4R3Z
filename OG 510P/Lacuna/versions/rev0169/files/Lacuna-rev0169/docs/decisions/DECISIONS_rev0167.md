# Decisions — rev0167

## D167-01 — add a post-primary-rating masking stage

**Decision.** Insert `awaiting-masking` between primary blind ratings and unblinding.

**Why.** Method-identifiability is useful feedback, but it is not the same thing as primary story quality. It must be recorded after primary ratings are frozen and before true condition labels are exposed.

## D167-02 — require assessor identity to match the primary rater

**Decision.** A masking assessment can be recorded only for an assessor ID that already appears as a primary rater.

**Why.** This supports paired analysis of one rater’s quality score and method recognition while preventing late addition of unpaired recognizers after seeing early outcomes.

## D167-03 — keep correctness out of masking artifacts

**Decision.** Masking artifacts carry guesses, cues, confidence, familiarity, and recognition flags. Correctness is computed only in unblinded reports.

**Why.** The masking phase is still blind. Joining true labels into that artifact would collapse the separation it is meant to measure.

## D167-04 — bind masking artifacts into bundle seals

**Decision.** Block-seal v3 includes masking artifact digests and bundle sealing requires children to be fully ready to unblind under the new definition.

**Why.** A public block seal should cover everything that was fixed before unblinding, not only primary ratings.

## D167-05 — close direct child unblind with a parent-opened gate

**Decision.** Bundle-staged child runs carry a closed unblind gate. The bundle parent opens it with a block-seal digest during all-block unblinding.

**Why.** Detecting premature direct child unblind after the fact is weaker than refusing the operation at the child boundary.

## D167-06 — keep the change descriptive, not inferential

**Decision.** Reports summarize method-identifiability counts and confidence sums but do not adjust primary ratings or claim bias correction.

**Why.** Whether recognizability mediates preference is an analysis question outside the custody kernel.
