# Scenario — progress hidden on pipes and prompts requiring TTY need explicit terminal posture

This scenario exists to stop future passes from collapsing these claims into one vague “works in terminals and CI” story:

- TTY detection decides whether progress renders,
- color policy may follow environment and terminal capability,
- prompts may require a terminal,
- and the non-interactive path may need explicit override flags.
