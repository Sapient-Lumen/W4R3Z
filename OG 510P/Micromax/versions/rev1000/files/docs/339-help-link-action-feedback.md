# Help link action feedback (rev397)

The docs/help browser already had the right tiny link workflow:

- `helpfollow` could jump to local docs targets or hand external URLs off to the same safe open-url confirmation surface as `urlopen`
- `helplinkcopy` could copy the markdown link target under cursor
- confirmation mode already knew whether the request came from `help`, `cursor`, or `command`

But one wording seam still lingered at that boundary:

- direct docs-buffer copy said `help: copied link target`
- confirmed external opens collapsed to `opened external link`
- confirmation-copy fell back to a generic multi-line `copied link` block

Rev397 keeps the fix deliberately small:

- direct docs-link copy now says `helplinkcopy: TARGET`
- confirmed external docs-link opens now say `helpfollow: URL`
- confirmation-copy now reuses `helplinkcopy:` for help-driven links and `urlcopy:` elsewhere

This matters because docs browsing is part of the same headless-first command/help surface as ordinary URL commands. Link actions should be attributable in logs, tests, and future LLM traces without making readers infer whether the URL came from docs help, under-cursor text, or an explicit command.
