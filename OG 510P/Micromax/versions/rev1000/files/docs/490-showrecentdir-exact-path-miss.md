# Rev548 — `showrecentdir` path misses stay exact before Enter too

## What changed

`showrecentdir DIR|N|#N` already reported exact recent-directory misses honestly after
Enter, and rev546 had already taught the command bar to keep visible-slot misses
like `#9` alive long enough to show `no such recent directory` before Enter.

This revision closes the sibling seam for typed directory paths. When you enter one
direct directory token like `showrecentdir /missing/project`, command completion now
preserves that raw token long enough to render the same exact-miss truth it would
show after Enter instead of falling back to a generic exact-inspector hint.

## Why it matters

Micromax is trying to keep inspectable command loops honest. Once the editor can
already tell that `showrecentdir` is being asked for one exact recent-directory
name, the command bar should say `no such recent directory` before Enter instead of
going generic or blank. That keeps the command-bar path aligned with the stable
after-Enter command message and makes the archive easier for future humans and LLMs
to trust.

## Verification

- completion row for `showrecentdir /definitely/not/a/recent-dir` now says
  `no such recent directory`
- `showrecentdir /definitely/not/a/recent-dir` still reports
  `showrecentdir: no such recent directory: /definitely/not/a/recent-dir` after
  Enter
