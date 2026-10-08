# Rev379: plain `markjump` miss feedback

Micromax already made named-mark navigation explicit on success:

- `mark NAME` reports the anchored target
- `markjump NAME` reports the landed target
- `markpick` reports both the queried miss case and the landed target

But one tiny seam still lingered in the same loop: the direct command-path miss still said `markjump: unknown mark NAME`. That was accurate, but it was weaker than the newer `no such ...` dialect used by nearby inspection and navigation commands, and it mismatched `markpick`'s own `no such mark` wording.

Rev379 keeps the implementation deliberately small:

- `markjump NAME` now fails as `markjump: no such mark: NAME`
- successful jumps still say `markjump: NAME -> target @ line:col`
- focused tests now pin down both the landed-target and missing-target paths

This is a trust/flow tweak more than a feature. Named marks are part of the editor's headless-first recovery loop, so they should fail in the same plain-spoken dialect as buffers, bindings, hooks, words, and other inspectable navigation targets.
