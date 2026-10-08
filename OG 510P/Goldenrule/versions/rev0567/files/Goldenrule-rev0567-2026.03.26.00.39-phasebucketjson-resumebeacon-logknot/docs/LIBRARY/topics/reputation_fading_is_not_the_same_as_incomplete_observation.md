# Reputation fading is not the same as incomplete observation

Recent indirect-reciprocity work adds a compact but important distinction for Concord's future reputation lanes.

- `RS-GR-136` separates two information limits that are easy to collapse by mistake:
  1. **incomplete observation**, where donor actions are seen only probabilistically; and
  2. **reputation fading**, where a recipient can become effectively **Unknown**.
- The paper reports that these two limits do **not** behave the same way.
- Under incomplete observation, the cooperation condition can remain unchanged because less frequent updates are offset by higher reputational stakes.
- Under reputation fading / `Unknown`, cooperation becomes harder and requires a higher benefit-to-cost ratio.
- The paper also reports that costly punishment can help under reputation fading, which means sanction results can depend on *which* information failure the world instantiates.

## Why this matters for Concord

A future world should not compress all imperfect-information reputation lanes into one “noisy reputation” toggle.

If agents simply miss some observations, that is one institution.
If agents can drift into an `Unknown` state, that is a different institution with different cooperation and punishment behavior.

Those are not presentation details.
They change what benchmark outcomes mean.

## Minimal implementor handoff

When Concord adds a reputation lane, the world contract should declare separately:

1. action-observation probability;
2. whether reputations can become `Unknown` / fade / expire;
3. the rule that creates or clears `Unknown` status;
4. whether punishment exists, what it costs, and whether it targets `Unknown` states differently.

Without that split, future results can mix two genuinely different institutions under one label.
