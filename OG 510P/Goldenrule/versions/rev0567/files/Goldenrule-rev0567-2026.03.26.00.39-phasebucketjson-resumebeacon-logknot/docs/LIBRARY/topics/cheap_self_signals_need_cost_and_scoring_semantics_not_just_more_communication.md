# Cheap self-signals need cost and scoring semantics, not just more communication

Recent work adds a second missing layer to Concord's communication worlds: **not every prosocial-looking signal deserves equal institutional weight**.

- `RS-GR-174` shows that in indirect reciprocity, post-hoc reputation signaling can become dishonest when signaling is cheap, especially when people can refuse help to a bad partner and then signal cooperativeness afterward.
- `RS-GR-175` shows that promise effects depend on active commitment rather than on weak, passive wording alone.
- Together with `RS-GR-140`, this implies that communication channels can be either genuine repair / commitment instruments or low-cost self-presentation channels, depending on how they are wired.

## Why this matters for Concord

A world that permits self-signaling after behavior is under-specified if it only says:

> agents can send messages.

It also needs to say whether signals are costly, whether they are scored independently from observed action history, and whether follow-through is checked.
Otherwise cheap self-presentation can look like repentance, trustworthiness, or stable cooperation when it is actually a low-cost attempt to rewrite reputation.

## Minimal implementor handoff

If Concord adds post-hoc explanations, self-descriptions, declarations of intent, or other reputation-facing signals, publish at least:

1. signal timing relative to the action it comments on;
2. whether sending the signal is free, effortful, scarce, or rate-limited;
3. whether observers evaluate the signal separately from the underlying action record;
4. whether signals can repair reputation only with follow-through or merely by being uttered;
5. whether the world includes at least one no-signal baseline.

Without that compact contract, future inheritors can mistake cheap impression management for moral or strategic improvement.
