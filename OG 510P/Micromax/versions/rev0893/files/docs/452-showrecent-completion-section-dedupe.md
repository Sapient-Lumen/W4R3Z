# Exact showrecent completion section dedupe

Rev510 closes one more tiny taste/trust seam in Micromax's exact recent-file
inspection loop inside the command bar.

Micromax already had the right nearby recent-file behavior:

- plain `showrecent PATH` reused the exact recent-file detail row instead of
  forcing humans or scripts to scrape the broader `recent` inventory
- palette `Recent Files` rows already kept their info slot focused on landing
  context plus tiny disk/action truth
- top-level recent-file command/palette surfaces already knew not to repeat the
  same root twice

But one tiny completion seam still lingered beside those surfaces:

- exact `showrecent PATH` completion rows kept the visible section in their
  menu as `#N /root`
- for top-level files, the info slot could still immediately fall back to
  `section=/root | existing file | current buffer`
- the repeated root added no new location truth because the completion row had
  already named that section in its menu

## What landed

Rev510 keeps the follow-up deliberately small.

- exact `showrecent` completion now reuses `Editor._recent_location_parts(...)`
  instead of rebuilding its info text from the raw detail field
- that completion path now trims one leading `section=/root` echo when the menu
  already names the same visible section
- the generic `inspect exact recent file` fallback now happens after disk/action
  cues are appended, so top-level rows can collapse all the way down to useful
  truth like `existing file | current buffer` or `switch buffer`
- focused tests pin both the existing nested-project case and the new top-level
  recent-file completion case

## Why this matters

This is another tiny command-bar taste/trust cleanup.

Once an exact completion row already says which recent-file section it belongs
to, repeating that same root again in the info slot just pushes the real disk
and action truth farther right. Keeping the row quiet makes the useful part
clearer without hiding anything important.

## Focused tests

- `tests/test_editor_prompt_completion_hostcalls.py`
