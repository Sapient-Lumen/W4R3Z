# Private reputation worlds need an explicit assessment-update rule

Recent indirect-reciprocity work adds a compact requirement for future Concord reputation worlds.

- `RS-GR-135` studies indirect reciprocity under **private assessment**, where agents do not all agree on who is good or bad.
- The paper finds that whether cooperation survives depends materially on **how images are updated**, not just on whether “reputation exists.”
- In particular, the authors report that some update priorities fail broadly, while a **good-image-prioritizing** update rule can sustain cooperation under several consistency functions.

## Why this matters for Concord

A future world that simply says “agents have reputations” is underspecified.
If assessments can disagree, then benchmark outcomes depend on at least:

1. whether assessments are public or private,
2. whether donor and recipient images are both updated,
3. which image wins when old and new evidence conflict,
4. and how noise / delay affect those updates.

Those choices are part of the institution, not just metadata around it.

## Minimal implementor handoff

When Concord adds a reputation lane, the world contract should declare:

1. visibility (`public`, `private`, or mixed),
2. update target set (donor only, recipient only, or both),
3. update-priority rule when assessments conflict,
4. observation / gossip latency and noise,
5. and which strategy hooks can read those image states.

Without that compact contract, “reputation helped” is too ambiguous to inherit safely.
