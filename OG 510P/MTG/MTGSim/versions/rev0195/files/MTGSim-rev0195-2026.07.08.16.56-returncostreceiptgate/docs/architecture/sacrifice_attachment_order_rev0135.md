# rev0135 Sacrifice Attachment Order — paying the legal set in a legal order

## Why this cut exists

rev0134 made the paid cast / activated ability body transactional: provisional stack objects, mana payment, tap costs, sacrifices, and stack-placement records live in a staged `GameState` until the body succeeds. The next audit found a more subtle semantic problem inside that protected body: the deterministic sacrifice-cost selector could choose a legal set of permanents, then pay them in an order that made a later selected object illegal.

The representative case is an attached Aura and the enchanted creature. A cost that can be paid by sacrificing both an enchantment and a creature has a legal payment order: sacrifice the attached Aura first, then the enchanted permanent. The old deterministic order followed battlefield order. If the creature appeared first, sacrificing it caused the Aura to go to the graveyard as attachment cleanup, so the later Aura sacrifice failed. rev0134 prevented that half-payment from leaking, but the semantic result was still wrong: a payable cost was rejected.

## What changed

rev0135 adds a narrow ordering helper for selected sacrifice-cost objects:

- `selected_attachment_depth(...)` computes how many selected attachment targets are above a selected object.
- `order_sacrifice_cost_objects_for_payment(...)` sorts selected objects so attached permanents are paid before selected objects they are attached to.
- `pay_selected_sacrifice_cost(...)` validates the selected set before mutation, then uses the attachment-safe order for the actual sacrifices and the human-readable payment detail.

This keeps the selector deterministic while avoiding a false rejection for legal attached-object payment sets.

## Regression

`test_sacrifice_cost_orders_attached_permanents_before_enchanted_sources` builds an attached `Tether Aura` on `Anchor Bear`, then casts `Severing Rite`, whose cost can sacrifice one creature and one enchantment. The regression proves:

- the cast succeeds;
- the spell reaches the stack;
- the Aura is sacrificed explicitly rather than being swept to graveyard when the creature leaves;
- the enchanted creature is sacrificed after the Aura;
- exactly three zone-change records are created for the cast and the two explicit sacrifices;
- the payment log exposes the attachment-safe sacrifice order.

## Relationship to the transaction spine

This is not a replacement for the paid-action transaction helper. It is the next layer inside it. The rev0134 transaction made partial payment safe to reject; rev0135 makes one class of payable staged payment succeed by choosing a legal internal order. The combination is the intended direction for the semantic kernel: stage first so failed internal refactors cannot leak, then refine each internal phase until the reducer is not merely atomic but rules-correct.

## Remaining gaps

The helper is deliberately narrow. It does not yet model explicit player choice among sacrifice candidates, simultaneous-cost declarations, replacement effects that modify sacrifice events, cost reductions/increases, or full cost-component phase evidence. Those belong in the future named paid-action phase model. The acceptance target remains: legal cost sets should be paid in a deterministic legal order when the scaffold can infer one, and failed cost attempts should leave the caller-visible StateCore unchanged.
