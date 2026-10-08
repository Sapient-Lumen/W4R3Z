# Evaluation protocol

LLM self-judgment is useful only as a biased instrument whose bias is visible.

## Required controls

1. **Temporal firewall**: do not judge work in the turn it was generated.
2. **Pairwise before absolute**: compare drafts or poems directly before issuing a band.
3. **Order swap**: reverse positions and check whether the verdict flips.
4. **Criterion-first**: judge form integrity, image pressure, diction risk, closure, specificity, and disclosure survival before a holistic band.
5. **Coarse bands**: use `S`, `A`, `B`, `dead`, not fake decimal precision.
6. **Disclosure gate**: for external-facing tests, blind rating may precede disclosure, but disclosure must be part of the test design.

## Suspicious verdicts

- Comfortable unanimous praise on strange work.
- Praise that names the project doctrine more than the poem.
- Preference for longer explanation over sharper poem.
- Verdicts that flip under order swap.
- Judgments that punish difficulty merely because it is difficult.

Record these as judge failures, not poem failures, until the evidence says otherwise.


## rev0012 note

The human selected high-risk machine-native work. P0001 now exists as `draft_001` using `FORM-branch-selector-diptych`; it is unjudged and cannot be promoted in the drafting turn.
