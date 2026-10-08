# Micromax language spec sketch (non-normative, WIP)

This is where we gradually turn design notes into something closer to a spec.

## 1. Lexing / tokenization
- whitespace-separated tokens
- symbols: `: ; [ ]`
- strings: double quotes with escapes
- comments:
  - `\` to end of line
  - `( ... )` non-nesting; preserved as `comment` tokens

Docstrings:
- If one or more `( ... )` comments appear at the start of a colon definition body,
  they are captured as the word’s `doc`.

## 2. Evaluation model
- tokens are read left-to-right
- integers/strings push literal values
- words are looked up in the current search order and executed
- `[` begins quotation collection until matching `]`
- `:` begins a colon definition until `;` (definition added to CURRENT wordlist)

Execution tokens:
- `' name` parses the next word name and pushes its execution token (xt).
- `execute` runs an xt.

## 3. Dictionary / namespaces
- wordlists identified by integers
- search order is an ordered list of wordlists
- CURRENT determines where new definitions are installed

Modules (rev5 convenience layer):
- `module NAME ... endmodule` creates a named wordlist and temporarily makes it current + searched.
- `use NAME` adds a module’s wordlist to the search order.
- `in NAME` sets CURRENT to a module.

## 4. Errors
- errors are structured (message + code + optional source span + trace)
- `catch` restores stack on error and returns an error code

## 5. Host boundary
- host functions are registered by the host (allowlist)
- `hostcall` invokes only allowlisted host functions

## 5.1 Data values (rev5)

In addition to integers, strings, quotations, and cells, micromax supports host-value **lists**.

- `list` creates an empty list.
- `push pop len nth set-nth clone` operate on lists.

## 5.2 Hooks (rev5)

Hooks are words that run an ordered list of callback xts.

- `hook NAME` defines a hook word.
- `hook-add` / `hook-rm` / `hook-clear` mutate hook handlers.
- `hook@` returns the handler list.

## 5.3 Return stack (rev11)

Micromax exposes a separate **return stack**.

- `>r` moves a value from the data stack to the return stack.
- `r>` moves a value back.
- `r@` copies the top return-stack value.
- `rdrop` drops the top return-stack value.
- `rdepth` reports return-stack depth.

(Note: in full Forths, locals may share return stack space; micromax locals are a
separate runtime structure, so these are always safe.)

## 5.4 Small combinators (rev11)

Micromax includes a few quotation combinators aimed at reducing stack gymnastics:

- `dip` executes a quotation while temporarily removing a value.
- `keep` executes a quotation with a value available, and then restores that value.

## 6. Safety
- step budgets can bound evaluation cost
- budget exhaustion raises a structured error with code `-100`

File loading:
- `include` loads and evaluates a file.
- `require` loads at most once per VM instance.

(Everything above will evolve; this file is the place we make it explicit.)
