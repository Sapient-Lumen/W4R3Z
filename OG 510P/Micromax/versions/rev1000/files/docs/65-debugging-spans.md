# Debugging: source spans and introspection

Micromax is designed to be hacked on by hand, offline. That only works if debugging is *pleasant*.

A key ingredient is **source spans**: most tokens carry `[filename line col]` metadata, and errors
(and tooling) can use that to point at the exact spot in a file.

## What has a span?

- Every token produced by the tokenizer has a `Span(filename, line, col)`.
- Quotations (`[ ... ]`) store the span of their opening `[`.
- Colon words (`: name ... ;`) store the span of the `:` token.
- Primitives typically have no span (they are "built-in").

## Errors show a caret excerpt

When the VM raises a `MicromaxError`, `VM.format_error()` tries to include:

- `filename:line:col` prefix
- the source line at that location
- a caret pointing at the column

The VM keeps a simple `sources` cache keyed by filename (populated on `eval()`), which makes
this work even when running scripts from in-memory strings.

## `xt-span` and friends

The core introspection word `xt-span` returns the source span of an execution token:

- `xt-span ( xt -- [file line col] | 0 )`

Return value policy:

- quotations and colon words return `[filename line col]`.
- primitives and other span-less values return `0`.

This is intentionally *portable*: it uses only lists/ints/strings.

### Example

```
: foo 123 ;
' foo xt-span  \ => ["<input>", 1, 1]

[ 1 2 + ] xt-span \ => ["<input>", 3, 1]
```

## Why this matters for the editor

In micromax-editor, commands, keybindings, plugins, and hooks become *data* that evolves live.

Spans make it feasible to:

- show "where did this keybinding come from?"
- build a reload debugger (re-run just the file that defined a word)
- attach breakpoint-like tooling at source locations

The span contract is small and should stay stable as we port the VM to Rust/WASM.

## `here-span` and `vm.last_span`

Sometimes you want the **call-site** span of *the currently executing word*.
Micromax tracks a best-effort `vm.last_span` (updated on each executed token / bytecode instruction)
and exposes it as:

- `here-span ( -- [file line col] | 0 )`

This is primarily an embedding/provenance tool. The editor uses it to attach spans to
*dynamically registered* things like micromax-defined command-bar commands.

## `xt-src` and `xt-src-rows`

When you have an execution token (XT), you often want a single, stable description of what it *is*.

- `xt-src ( xt -- s )` returns a best-effort multi-line source view (definition-ish first line + `\\` metadata lines).
- `xt-src-rows ( xt -- rows )` returns structured rows `[[text kind span|0] ...]` so UIs and tooling can render the same information without parsing free-form text.


## Missing-word introspection feedback

The oldest VM-side introspection words now fail plainly when the requested word is absent:

- `help foo` -> `help: no such word: foo`
- `see foo` -> `see: no such word: foo`
- `where foo` -> `where: no such word: foo`

That keeps offline REPL debugging aligned with the editor's newer plain-spoken inspection commands: the miss tells you which tool failed, not just that a bare name could not be resolved.

## `callstack` / `trace`

For low-friction debugging (especially from hosts/UIs), Micromax exposes the VM's
best-effort call chain as a plain list of strings:

- `callstack ( -- xs )`
- `trace ( -- xs )` (alias)

`xs` is ordered from outermost to innermost word name.

Notes:

- This is not a full return-stack dump; it's the VM's *execution* call chain.
- The list intentionally excludes the `callstack` word itself when present.
