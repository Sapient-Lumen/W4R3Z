# Modal spells and choices through rev0021

rev0021 adds the first executable scaffold for modal spells. The goal is not to implement every modal card. The goal is to make the engine carry an explicit mode choice from legal-action generation, through casting, onto the stack, into validation, and finally into selected-mode resolution.

## Current model

- `SpellModeDefinition` stores a mode name, effect kind, amount, optional counter kind, optional target mask, and optional token-definition index.
- `CardDefinition::modes` marks a fictional sample card as modal.
- `GameObject::chosen_mode_index` records the selected one-based mode while the object is on the stack.
- `LegalAction::mode_index` lets the action API expose distinct cast choices for search, fuzzing, and future ML action masks.
- `cast_from_hand_to_stack_paying_mana_with_mode(...)` validates the chosen mode, pays the simple mana cost, chooses a target only if that mode requires one, then moves the object to the stack.
- `resolve_top_of_stack(...)` dispatches the chosen mode's payload. An illegal sole target at resolution produces no effect in this scaffold.

## Scenario syntax

Scenario cards can define modes with repeated `mode=` fields:

```text
card "Sample Charm" instant 0 0 cost=R mode=Spark:damage:2:any mode=Mend:gain_life:4:none
```

Casting can specify mode and target in either order:

```text
action cast_paid 1 1 mode=1 target=player:2
expect_mode 1 1
```

Untargeted modes omit `target=`:

```text
action cast_paid 1 1 mode=2
```

## Validation rules

Validation rejects modal state that should never persist:

- a chosen mode on an object outside the stack;
- a modal stack object without a mode;
- an invalid mode index;
- targets stored for an untargeted selected mode;
- a missing target for a targeted selected mode;
- a chosen mode on a nonmodal stack object.

`move_object(...)` clears chosen-mode metadata when an object leaves the stack, matching the existing cleanup behavior for target refs and combat metadata.

## Extensibility reason

Modes are a useful pressure test for the whole engine shape. They force the engine to avoid a single `CardDefinition::effect_kind` assumption and instead ask: what choice did the player make, what target group belongs to that choice, and what payload should resolve? That is the same style of seam needed for kicker, escalation, split cards, modal double-faced cards, triggered ability choices, and ML action masks.

## Known gaps

This is a one-mode, one-target-group scaffold. It does not yet implement choosing multiple modes, repeated mode limits, entwine/escalate/additional costs, modal abilities, triggered ability modes, target-changing effects, partial illegal target resolution, Oracle-text-derived mode parsing, replacement/self-replacement effects that care about modes, modal double-faced card selection, or full casting-rule ordering.
