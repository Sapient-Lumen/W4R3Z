# Scenario — miette URL exists but recipe witness is missing

A crate emits a `miette` diagnostic code/help/URL pointing users to a docs page, but the linked smallest-good-path example is not exercised in CI.

Why it matters:
- `miette` gives a valuable structured support channel,
- but a clickable URL is not the same thing as a witnessed recovery path,
- so channel truth and recipe witness must stay separate review objects.
