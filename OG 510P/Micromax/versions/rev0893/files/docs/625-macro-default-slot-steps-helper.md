# Rev684 - centralize default-slot step counts behind one helper

Micromax now has several tiny macro summaries that all speak in the same default-slot language: `default=last (N step[s])`, play-root action rows, and record-root action rows. They all need the same answer to a very small question: how many steps are currently in `last`?

Rev684 keeps the follow-up deliberately small and structural. New `_macro_default_slot_steps()` now owns that fetch once, and the step-aware label/play-root/record-root helpers reuse it instead of each reparsing `macro_detail_row('last')` for themselves. Visible behavior stays the same; the goal is simply to make future default-slot wording changes less drift-prone for humans and LLMs working in this archive.
