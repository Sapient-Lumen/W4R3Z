# Pattern calibration controls

Revision: rev0019

Pattern records are tempting because they make the cube feel intelligent. They are also dangerous: a pattern can become a confirmation-bias machine if it only receives examples that fit.

Rev0019 introduces `CTL` records so future sessions can add controls without pretending they are negative results. A positive control says: “the pattern must not overgeneralize past this.” A negative control says: “the pattern must not absorb this non-example.” A counterexample says: “the pattern may be wrong or too broad.”

For `MKH-PAT-0015`, rev0018 had three disconfirming/denominator-pressure records. Rev0019 adds three positive controls. The result is not maturity; it is a better question:

> Under what conditions do candidate mechanisms fail, survive, become clinically actionable, or require new denominator rails?
