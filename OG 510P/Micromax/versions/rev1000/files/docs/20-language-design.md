# Micromax language design (proposal v0)

This is not a conformance spec. It’s the evolving “shape” of the language we want.

## Core vibe
- concatenative, stack-based
- words are the unit of extension
- quotations `[ ... ]` are first-class (“code as data”)
- namespaces via wordlists + explicit search order
- guardrails appropriate for being a plugin system

## Data model (today)
- integers
- strings
- quotations
- cells (mutable single-slot storage; used for variables and deferred words)
- execution tokens (xt): a **word** or a **quotation**

## Execution tokens (xt)
Why: editor keymaps/callbacks want “a thing you can store and run later”.

- `' name` parses the next word name and pushes its xt
- `execute` runs an xt
- quotations are also xts (run via `execute` or `call`)

## Deferred words (dynamic hooks)
Why: editor architecture often wants “a hook point” that plugins can replace.

- `defer name` defines a deferred word (initially unset)
- `' foo is name` sets a deferred word from an xt
- `defer@` / `defer!` allow explicit get/set using xts on the stack

## Control flow
Runtime control is quotation-based:
- `if ( flag qtrue qfalse -- )`
- `when ( flag q -- )`
- `while ( qcond qbody -- )`

(We keep control flow explicit and debuggable; no hidden compiler state.)

## Errors
- `catch ( q -- ior )` executes a quotation, restoring the stack on error
- `throw ( ior -- )` raises if nonzero
- `last-error` returns a formatted string (source span + trace when available)

## Namespaces
Wordlists + search order:
- each plugin gets its own wordlist
- host/editor APIs can live in dedicated wordlists
- search order conventions become part of “plugin hygiene”

See: `docs/12-landscape-and-adjacencies.md` and `docs/41-decisions-log.md`.

## Safety rails
- script budgets (`set-budget`, `with-budget`) for cooperative/local limits
- separate embedding-owned host budgets when code being limited must not control
  the limiter; every active host frame consumes dispatch steps
- hostcalls are allowlisted (`hostcall`) and can be further capability-gated

Instruction budgets cannot preempt a blocking/expensive hostcall, bound memory
inside one primitive, or isolate native/process failure.

## Near-term design questions
- stack effect annotations (documentation first; now inspectable via `xt-effect` / `words-rows`, later tooling/checking)
- module/import conventions for plugins (wordlist + load order conventions)
- richer data (maps/records) vs “keep it tiny”
- cooperative tasks (yield/scheduler) vs “host-managed only”
