# Actor identifiability and action visibility should be separate world fields

Recent work adds a missing disclosure layer for Concord's future cooperation worlds: **seeing who someone is is not the same as seeing what they did**.

- `RS-GR-159` reports that when individual contributions remain private, merely disclosing group members' identities can reduce cooperation.
- The paper further reports that this drop is especially strong when identified group members are socially distant from one another.
- `RS-GR-160` adds that identity cues and reputation cues interact rather than simply add.
- The paper reports that face and name information can modulate how people respond to the same reputation signal, including softening or blunting the behavioral effect of a bad reputation.

## Why this matters for Concord

A benchmark should not collapse these disclosure choices into one vague transparency knob.

There is a real institutional difference between:
1. anonymous actors with visible actions;
2. identifiable actors with private actions;
3. identifiable actors with action-linked public histories;
4. weak identity cues (stable handle) versus strong identity cues (name, face, category label).

Those choices do not merely change presentation.
They change whether reputation sticks, whether social distance or favoritism enters the game, and whether a behavior change is driven by action evidence or by identity cues that modulate the reading of that evidence.

## Minimal implementor handoff

When Concord adds richer cooperation, helping, or reputation lanes, the world contract should declare:

1. whether actors are anonymous, pseudonymous, stable-handle, or strongly identifiable;
2. whether actions are publicly visible, privately logged, selectively visible, or unlinkable to identity;
3. what identity cues are revealed (name, avatar, face, group tag, model family, provider, or none);
4. whether identity information appears before behavior, after behavior, or only through accumulated history.

Without that publication layer, future results can mistake identity exposure, social distance, or label effects for genuine reciprocity gains.

