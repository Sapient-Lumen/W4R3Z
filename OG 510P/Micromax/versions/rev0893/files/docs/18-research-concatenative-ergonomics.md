# Concatenative ergonomics (notes)

This is a grab-bag of features that make a “gorgeous forth” feel *pleasant* at
scale, especially when the goal is editor scripting.

Primary sources referenced here:

* Factor docs: stack effects, including quotation parameters + row variables:
  https://docs.factorcode.org/content/article-effects.html
* Factor tutorial snippet on stack effect checking:
  https://andreaferretti.github.io/factor-tutorial/
* Factor docs: namespaces/dynamic variables:
  https://docs.factorcode.org/content/vocab-namespaces.html
* Gforth manual: Standard Forth locals overview:
  https://gforth.org/manual/Standard-Forth-locals.html
* Forth200x locals proposal:
  https://www.forth200x.org/locals.html

## 1) Stack effects as *real* metadata (not just comments)

Factor uses stack effect notation everywhere and can do consistency checks.
It also supports combinators whose behavior depends on the stack effects of
quotation parameters (row-polymorphic effects).

Micromax today:

* preserves leading paren comments as docstrings
* has quotations and combinators like `while`

Micromax soon (proposal):

* parse a leading stack-effect comment like `( x y -- z )` and store it as
  structured metadata
* start with **arity checking** in debug mode (optional)
* later: allow "row variables" (`..a`) in effects for higher-order words

## 2) Locals: keep the stack, but let humans breathe

Standard Forth has locals that are initialized from the stack, and accessed by
name.

Micromax today:

* has lightweight locals sugar: `->name` stores, `name` loads

Next (proposal):

* add a *declaration* form for clarity in longer words, inspired by Forth200x
  locals syntax, but keep it optional.

## 3) Namespaces / vocabularies to stop plugin ecosystems from rotting

Factor has strong vocabulary/namespacing culture and a notion of dynamic
variables/namespaces.

Micromax today:

* wordlists + search order
* `module ... endmodule` for scoped namespaces

Micromax-editor today:

* one wordlist per plugin

## 4) Combinators are the “standard library”

Joy/Factor traditions put a lot of power in combinators (higher-order words that
take quotations). This is a natural fit for:

* keybinding macros
* editor hooks
* "do this with a prompt" flows

Micromax today:

* quotations + `call`
* basic combinators (`if`, `when`, `while`)

Next (proposal):

* add small combinators with big leverage: `dip`, `keep`, `bi`, `tri`, `2dip`, etc.
* add a minimal sequence protocol for lists (map/filter/reduce)
