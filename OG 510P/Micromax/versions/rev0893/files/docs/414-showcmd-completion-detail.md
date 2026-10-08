# Rev472 — `showcmd` completion now reuses exact command detail rows

Micromax already had the right exact command-inspection substrate: `showcmd NAME`
reported one command's doc/group/provenance for humans, and
`command_detail_row(NAME)` / `ed.command-detail-row` exposed the same tiny
`[name doc group|0 [file line col]|0]` register for scripts and future UIs.

But one small command-bar seam still lingered next to that exact row: selecting a
visible command for `showcmd ...` still collapsed back to a thinner completion row
that only showed the doc string. That meant the prompt hid where a command came
from precisely when future humans/LLMs were deciding whether a visible command was
built in, plugin-provided, or locally registered.

This rev keeps the follow-up deliberately small:

- add a shared `_prompt_command_row(...)` helper that reuses `command_detail_row(NAME)`
- make `showcmd NAME` completion reuse that exact row instead of a generic
  `inspect command` placeholder
- keep command docs in the visible menu slot and move group / definition provenance
  into the prompt info slot
- pin the contract with a focused prompt-completion test

The goal is simple: if one command already has one tiny honest exact row,
`showcmd` completion should reuse it too instead of downgrading that metadata at
selection time.
