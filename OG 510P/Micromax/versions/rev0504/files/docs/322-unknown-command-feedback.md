# Unknown command feedback stays command-specific

Small trust/flow follow-up: the ordinary command-bar typo path used to say
`Unknown command: NAME`, which was understandable but out of dialect with the
rest of the newer inspection/navigation feedback.

Micromax now reports:

- `command: no such command: NAME`

Why this tiny change matters:

- it keeps the command family visible at the exact point of failure
- it matches nearby command-oriented inspection feedback like
  `showcmd: no such command: NAME`
- it gives future UIs/scripts/LLMs one plainer command-miss dialect instead of
  a special-cased capitalized sentence

This is intentionally small. The command bar should fail as plainly as the
inspection paths around it.
