# Rev552: advertise `recent #N` in the command/help doc

## Why

Micromax already accepted visible recent-slot tokens on the real command path:

- `recent N` reopened the Nth MRU entry
- `recent #N` reopened the same visible slot in the picker/inventory dialect
- command-bar completion already previewed exact visible-slot misses like `recent #9`
- rev551 just aligned executed missing-slot feedback with that same `no such recent file` truth

But one tiny source-of-truth seam still lingered in a central place humans and future LLMs rely on:

- the registered command/help doc still said `recent [N|clear] - show/open recent files`

That made one real exact-input path look unofficial even though the implementation had already stabilized around it.

## What changed

Rev552 keeps the change deliberately tiny:

- update the registered dispatcher/help doc to `recent [N|#N|clear] - show/open recent files`
- let command-bar command rows inherit that corrected doc automatically
- pin the updated command-row contract in focused tests
- refresh the archive breadcrumbs/context so future readers see `#N` as first-class recent syntax

## Result

If Micromax visibly accepts `recent #N`, the command/help surface now says so plainly. The recent-file loop no longer asks humans or future LLMs to infer one stable input dialect from neighboring behavior.
