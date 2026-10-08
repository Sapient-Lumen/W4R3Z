# Official voter-information disabled-control surface checklist

Use this checklist for official voter-information routes where **the public can see a next-step control or option, but that control is currently unavailable or disabled**.

## Unavailable-state truth review

- [ ] Record which visible controls or options on the route can become unavailable or disabled.
- [ ] Review whether each unavailable state explains why the control is unavailable.
- [ ] Review whether each unavailable state explains what prerequisite, timing condition, or scope condition would enable the control.
- [ ] Review whether the route distinguishes a not-yet-enabled state from a real “not permitted” or “no such option” answer.
- [ ] Review whether any unavailable state is actually standing in for missing guidance, missing validation, or unclear routing that should stay visible instead.

## Semantics, discoverability, and recovery

- [ ] Review whether native `disabled` is used only when removing focus/submission is the right public consequence.
- [ ] Review whether `aria-disabled` is paired with scripted suppression and visible styling when the route needs users to still discover the unavailable action.
- [ ] Review whether keyboard and assistive-technology users can still perceive important unavailable actions and their reason text.
- [ ] Review whether helper text, inline validation, or same-page correction is preferred when the user can still resolve the blocker on the current page.
- [ ] Review whether compact/mobile layouts preserve the unavailable reason and unlock path instead of leaving only a greyed control visible.

## Fallback and evidence review

- [ ] Review whether the route provides a truthful help, overview, or fallback official path when the blocker cannot be resolved on the current page.
- [ ] Review whether grouped control lanes make it clear which actions remain available and which are presently unavailable.
- [ ] Preserve a small public digest of which unavailable controls were reviewed, why they were unavailable, and what unlock or fallback path controlled.
- [ ] Do not retain individualized click-abandonment logs, session replay, or similar frustration exhaust merely to prove that a control was once disabled.
