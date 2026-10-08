# Micromax Tutorial (draft)

This is a **pedagogy-first** introduction to micromax.

Micromax is a small, embedded, concatenative language (Forth-inspired, not standards-bound).
The long-term “first big object” we want to build is a *terminal text editor* whose config/plugins/macros
are written in micromax — but this repo focuses on the **language + VM** first.

## The mental model

Micromax is a *stack language*:
- values live on a data stack
- words (functions) transform the stack
- code is written as a sequence of words: `1 2 +` pushes 1, pushes 2, adds them

You’ll see stack effects written like:

`( a b -- c )` meaning: consume `a b`, produce `c`.

(We currently treat stack effects as documentation; later we may add dev-mode checking inspired by Factor’s
stack-effect system. They are now also exposed as introspection data via `xt-effect`, `xt-doc`, `help`, and `words-rows`.)

## Try it

Run the REPL:

```bash
python -m micromax.repl
```

Then:

```
mx> 1 2 + . cr
3
```

## Defining words

A colon definition:

```
: square ( n -- n2 ) dup * ;
```

Use it:

```
7 square .
```

Leading paren comments become docstrings/metadata:

```
: inc ( n -- n ) ( add one ) 1 + ;
help inc
```

You can inspect them directly:

```
' inc xt-effect   \ => "( n -- n )"
' inc xt-doc      \ => "add one"
words-rows         \ => rows like [name kind effect doc wid wl]
```

Inside the editor command bar, the same metadata is now surfaced through `help inc` (if no editor command/action named `inc` exists) and `showword inc`.

## Quotations (code as data)

Quotations are blocks written `[ ... ]`. Execute them with `call`:

```
[ 10 1 - ] call .
```

Quotations are values you can store and pass around — essential for editor keybindings, hooks, and callbacks.

## Runtime conditionals

Micromax’s `if/when/while` are **runtime** combinators that operate on quotations:

```
1 [ "yes" . ] [ "no" . ] if
```

## Small combinators that reduce stack gymnastics

Micromax’s stdlib keeps a tiny set of quotation combinators that are worth learning early:

```
4 [ 1 2 + ] dip                \ => 3 4
3 4 [ + ] keep                 \ => 7 4
100 200 [ + ] 2keep            \ => 300 100 200
5 [ 1 + ] [ 2 * ] bi           \ => 6 10
5 [ 1 + ] [ 2 * ] [ dup * ] tri\ => 6 10 25
```

These stay in stdlib rather than the VM primitive set, which keeps the core small and
portable while still making scripts noticeably nicer to write.

## Locals (ergonomic sugar)

Classic Forth is famously “stack-only”, but many Forth systems add locals for readability.
Gforth’s locals tutorial is a good reference point for what “locals in a Forth-ish language” look like:
`{ a b -- ... }` introduces locals whose names push their values. See:
https://gforth.org/manual/Local-Variables-Tutorial.html

Micromax uses **simple runtime sugar**:

- `->name` stores (pops) into a local named `name`
- `name` loads it later (locals shadow dictionary words)

Example:

```
: add2 ( n -- n ) ->x x 2 + ;
5 add2 .
```

Debug helpers:
- `locals` prints the current locals frame (debug)
- `locals-clear` clears the *session* locals (top-level)

## A slightly more “object-ish” style: `.word` and `send`

Micromax is still fundamentally word-based, but for ergonomics we support:

- `.foo` postfix sugar expands to `"foo" send`
- `send` executes a word by name (string), resolved through the current search order

Example (lists):

```
1 list push dup .len    \ leaves: [1] 1
```

Example (maps):

```
1 "count" map m! "count" swap m@    \ leaves: 1
```

This is “Smalltalk-ish message send” without committing to a heavy object system yet.

## Namespaces: wordlists and modules

Wordlists + search order are the core namespace mechanism (standard Forth approach).
Micromax adds a friendlier layer:

```
module foo
  : a 123 ;
endmodule

use foo
a .
```

## Hooks (multi-handler callbacks)

Hooks are words that run an ordered list of callbacks (xts).
This is inspired by common editor extension patterns (e.g., Emacs hooks):
https://www.gnu.org/software/emacs/manual/html_node/elisp/Hooks.html

```
hook on-save
: h1 1 ;
: h2 2 ;
' h1 hook-add on-save
' h2 hook-add on-save
on-save   \ pushes 1 then 2
```

## Files: include/require/reload

- `include` loads a file always
- `require` loads at most once (per VM instance)
- `reload` forces re-evaluation (building block for hot reload)
- `unrequire` forgets a required path

## Safety basics

- `catch` / `throw` for structured errors
- step budgets prevent “freeze the host” scripts

More in: `docs/60-concurrency-and-safety.md` and `docs/62-host-owns-world.md`.

## Tiny editor prototype (headless)

There is a deliberately minimal, unit-testable editor core in `src/micromax_editor/`.
It is **not** a full TUI yet; it’s a test harness that lets us iterate quickly.

Run it:

```bash
python -m micromax_editor
```

Try:

* `:cmd open myfile.txt`
* `:cmd replace 'foo' 'bar' -a -l`
* `:key Ctrl-e` then type `help` and `:enter`
* Selection/copy/paste: `:key Shift-RightArrow` … `:key Ctrl-c` … `:key Ctrl-v`



If you forget a name, the editor command bar now has `apropos QUERY`, which searches command names, action names, and visible Micromax words using the same tiny deterministic fuzzy ranking used by prompt completion. It is still name-first, but can now also rescue matches from topic summaries/docs. Likewise, `help NAME` now suggests a few likely topics when there is no exact match.

There is now also a dedicated searchable topic/help prompt:

- run `topicpick` (or `topicpick QUERY`) from the command bar
- or trigger the `TopicPrompt` action from a future keybinding/UI

That prompt preloads ranked topic rows, live-refreshes them as you change the query, lets `Tab` / `Shift-Tab` cycle them, and opens help for the selected/best-ranked topic when you press Enter. If you are scripting or prototyping a future UI, `ed.prompt-current-row` exposes the active item without redoing ranking yourself, `ed.topic-section-rows` / `ed.apropos-section-rows` expose grouped `Commands` / `Actions` / `Words` sections, and `ed.prompt-current-preview` gives you a small current-item summary string.
