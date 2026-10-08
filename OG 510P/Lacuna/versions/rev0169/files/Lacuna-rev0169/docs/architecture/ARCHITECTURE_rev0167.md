# Architecture — rev0167

## Purpose

Revision 0167 tightens the comparative scenario and bundle layers around a specific experimental weakness: after blind raters score transcript quality, they may still be able to identify the generation method from style, structure, artifacts, or leaked process cues. Rev0167 makes that a first-class, post-primary-rating and pre-unblinding artifact instead of an informal note.

The database remains schema 8 and immutable event envelopes remain schema 1. The new contracts are exchange/sidecar schemas for scenario runs, scenario bundles, reports, and block seals. No worker receives new story mutation, commit, checkpoint, or unblinding authority.

## Scenario run v3

A scenario run now walks this evaluation sequence:

```text
collect cell results
  → complete retained-tree contamination scan
  → build blind rating packet
  → freeze every primary blind rating
  → freeze every post-rating method-identifiability assessment
  → unblind and join correctness
```

The new `awaiting-masking` state sits between primary ratings and `ready-to-unblind`. Primary ratings are retained before any method guess artifact is accepted. A masking assessment receives the blind packet and the SHA-256s of all primary rating artifacts; it does not receive the answer key, bundle block seal, or condition mapping.

Each `lacuna.scenario-masking-assessment.v1` records, per blind cell:

- guessed condition, including `unknown`;
- confidence from 0 to 100;
- cue list;
- familiarity level;
- explicit recognized-method flag; and
- assessor notes.

The assessor ID must match a retained primary rater ID. This deliberately supports within-rater analysis without letting a new post-hoc assessor join the evidence after seeing primary outcomes.

## Scenario report v3

`lacuna.scenario-report.v3` retains primary rating artifact digests, masking artifact digests, and a method-identifiability summary. Correctness is computed only at unblinding, when the answer key is available. Reports now separate:

```text
ratings: primary blind outcome judgments
masking: post-rating method guesses and cues
unblinding: condition key plus correctness joins
```

The report can therefore distinguish “condition A was preferred” from “condition A was recognizable.”

## Bundle v2 and block-seal v3

Scenario bundles now pre-stage child runs with a closed unblind gate. Each gate is bound to the bundle ID and block ID and has no opening digest until the bundle parent has durably sealed every block and entered its all-block unblinding phase.

A bundle block can be sealed only after its child reaches `ready-to-unblind`, which now means all cell results, scan custody, primary ratings, and post-rating masking assessments are frozen. The block seal v3 includes masking artifact digests alongside the blind packet, ratings, contamination scan, and retained cell results.

During bundle unblinding, the parent opens each child gate with a digest of the corresponding block seal before calling the child unblind operation. Direct child unblinding before that point refuses with a closed-gate error instead of depending only on later parent audit detection.

## Bundle report v3 and rater-level exports

Bundle report v3 adds method-identifiability fields to every rater-level observation and to the descriptive summary by condition. CSV export now includes method guess, correctness, confidence, recognition/familiarity, and spreadsheet-safe cue text.

The bundle report keeps primary aesthetic/scenario ratings and masking judgments distinct. It does not claim that method recognition invalidates a rating; it makes the confound measurable.

## Authority boundary

Rev0167 adds no model invocation, vendor attestation, automatic rater recruitment, statistical inference engine, or proof of isolation. It records the post-rating masking evidence needed for later analysis and closes the most obvious direct-child unblind bypass in bundle-staged experiments.
