# Official voter-information tooltip/popover surface checklist

Use this checklist for official voter-information routes where **small hint bubbles, tooltips, popovers, or similar helper disclosures explain part of the answer or next step**.

## Meaning and trigger review

- [ ] Record which routes use tooltips, popovers, info-icon bubbles, or hover/focus help disclosures.
- [ ] Review whether each disclosure is truly supplemental or whether it carries meaning that controls task completion, route choice, or rule interpretation.
- [ ] Review whether the trigger looks interactive and is discoverable without guesswork.
- [ ] Review whether the same critical meaning appears in visible or otherwise durable text if it controls the voter’s decision.
- [ ] Review whether the disclosure is brief enough to fit a tooltip posture or whether it really belongs in a more durable disclosure pattern.

## Behavior, semantics, and collision review

- [ ] Review whether custom hover/focus disclosures are dismissible, hoverable, and persistent enough to read and compare.
- [ ] Review whether keyboard users can discover and dismiss the disclosure without losing context.
- [ ] Review whether touch/no-hover users can reach the same meaning without relying on long-hover browser behavior.
- [ ] Review whether non-interactive tooltip semantics are used only for brief non-interactive help, while more substantial disclosures use an explicit button-triggered popover/disclosure or other honest pattern.
- [ ] Review whether the disclosure covers or visually overwhelms the exact answer text or control it is meant to explain.

## Fallback and evidence review

- [ ] Review whether compact/mobile layouts preserve the same governing meaning without turning it into a clipped or hidden bubble.
- [ ] Preserve a small public digest of which tooltip/popover disclosures were reviewed, whether they were supplemental, and where the durable visible meaning lives if the content is important.
- [ ] Do not retain individualized hover telemetry, cursor heatmaps, session replay, or similar interaction exhaust merely to prove that a help bubble once existed.
