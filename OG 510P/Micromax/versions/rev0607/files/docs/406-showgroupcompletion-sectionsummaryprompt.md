# Rev464 — broad navigation summary completion now reuses tiny section-summary rows

## Why

Micromax's navigation surfaces had already grown a clean three-scale loop:

- grouped browse state (`bufferpick`, `recentpick`, `recentdirpick`, `markpick`)
- broad count-aware section summaries (`showbuffergroups`, `showrecentgroups`, `showrecentdirgroups`, `showmarkgroups`)
- exact one-target detail rows (`showbuffer`, `showrecent`, `showrecentdir`, `showmark`)

But one small flow seam still lingered in the ordinary command-bar loop. The broad summary commands already knew their visible section labels and already exposed tiny `[label count sample_name sample_detail]` rows, yet completion still treated those query slots as opaque text. Humans and future LLMs could inspect a bucket after guessing its label, but the prompt itself could not help them aim.

## What changed

Rev464 keeps the follow-up deliberately small:

- add a shared editor helper for the broad navigation summary commands' tiny section-summary rows
- let `showbuffergroups`, `showrecentgroups`, `showrecentdirgroups`, and `showmarkgroups` complete visible section labels
- reuse those same summary rows to populate `[insert kind menu info]` prompt metadata
- keep the prompt rows tiny and honest: count in `menu`, sample detail in `info`
- document the intent in the command-bar / completion / command docs so future humans and LLMs see that broad summary queries are inspectable too

## Result

Broad navigation summary commands now behave more like the newer exact-row commands:

- the prompt can suggest one known visible bucket directly
- choosing that bucket keeps small count/sample context visible
- completion stays aligned with the same substrate the human-facing summary command already uses

This is a small flow/trust move, not a new feature family. The command bar simply stops hiding metadata it already had.
