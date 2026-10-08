# Embedded language lessons (micromax rev5)

This doc is a *grab bag* of “what others already learned” about embedding a small language into a host
application (especially editors), plus what we’re copying into micromax.

## Embedding API is part of the language

Wren’s docs are blunt about this: the language is designed to live inside a host app, so the
embedding API is as important as the language itself.

- Wren embedding docs: https://wren.io/embedding/

**Micromax takeaway:** treat the host boundary as a first-class design surface.
We should keep it **small, capability-based, and testable**.

## “Small but actually usable” languages and what they optimize for

Janet is a good example of an embeddable language that still aims to be *pleasant* for real programs,
and it explicitly supports embedding.

- Janet guide (general): https://janet.guide/all/
- Janet C embedding docs: https://janet-lang.org/capi/embedding.html

**Micromax takeaway:** usability isn’t “batteries”; it’s *sharp edges removed*:

- meaningful errors
- simple data containers
- clear module boundaries
- safe-ish concurrency story

## Editor extensibility patterns: hooks and advice

Emacs’s extensibility often relies on **hooks** (a variable holding one or more functions called on
specific occasions) and **advice** (wrap/augment existing functions).

- Emacs Lisp “Hooks”: https://www.gnu.org/s/emacs/manual/html_node/elisp/Hooks.html
- Emacs Lisp “Advising Functions”: https://www.gnu.org/s/emacs/manual/html_node/elisp/Advising-Functions.html

**Micromax takeaway:** provide cheap “extension points” that do not require patching core words.

Rev5 implements **hooks** as a low-hanging fruit:

- `hook on-save`
- `' handler hook-add on-save`
- `on-save` runs all handlers (in order)

Advice is *planned* (likely via hook-like wrapper chains on words), but not implemented yet.

## Namespaces and search order matter immediately

The Forth-2012 “Search-Order” word set exists largely because global namespaces don’t scale.

- Search-Order word set: https://forth-standard.org/standard/search

**Micromax takeaway:** treat “module hygiene” as a baseline requirement, not a later refactor.

Rev5 adds a friendly module layer on top of wordlists:

- `module foo ... endmodule`
- `use foo` to import the module’s wordlist into the search order
- `in foo` to set the compilation/current wordlist

## Stack-effect checking and smart combinators

Factor’s docs show a pragmatic route to making concatenative code less spooky: stack effect
inference/checking, especially for combinators that take quotations.

- Combinator stack effects: https://docs.factorcode.org/content/article-inference-combinators.html
- Stack effect tools: https://docs.factorcode.org/content/article-tools.inference.html

**Micromax takeaway:** long-term, we want lightweight stack-effect metadata and a partial checker.
Rev5 starts with the *documentation format* (paren comments like `( a b -- c )`) so we can later
reuse it for checking.

## Concurrency: choose a boring story

Gforth documents both a cooperative multitasker and a pthread-based multitasker, and it notes that
real concurrency demands coordination to avoid conflicts.

- Gforth multitasker docs: https://gforth.org/manual/Multitasker.html

**Micromax takeaway:** for the editor target, assume:

- micromax runs plugin callbacks **cooperatively** on the UI/event thread
- background work is owned by the host and interacts via message passing
- all callbacks run under budgets (`with-budget`) and error trapping (`catch`)
