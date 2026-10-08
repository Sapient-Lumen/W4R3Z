# Scenario family — potentially untrusted filter input requires regex-off or manual review

This fixture family exists for crates that expose filter directives through operator input, HTTP configuration, admin panels, or other partially untrusted sources.

It is meant to catch support drift such as:

- the crate documents `EnvFilter`-style field matching as part of the official activation recipe,
- but leaves regex matching enabled for untrusted input,
- or treats an operator-supplied directive as a stable support path without recording the review boundary,
- or silently widens the attack/safety surface while still calling the recipe “safe by default”.

A good observability pack should make four things explicit:

1. whether filter input is maintainer-controlled or potentially untrusted,
2. whether regex matching is enabled or intentionally disabled,
3. whether the recipe remains official when regex stays on,
4. and where `manual_review_required` begins.

This family keeps “the filter syntax is powerful” separate from “the activation recipe is a trustworthy support contract”.
