# Vision

**Micromax** is a small, embeddable, concatenative language intended to be a *sane* plugin/config/macro system.

We’re building it “planning-first”:
- design + guardrails first
- a tiny Python VM so we can test/iterate inside the cloud container
- only after the language feels right do we build our first big target: a slim terminal text editor

## What makes micromax “Forth-inspired”
- tiny core vocabulary (“words”)
- interactive and redefinable
- composition via the data stack
- namespacing via wordlists/search order

## What makes micromax “not traditional Forth”
We will diverge wherever it improves:
- ergonomics for scripting (quotations/combinators are core)
- safety (budgets, hostcall allowlists, isolation conventions)
- debuggability (source spans + traces everywhere)

## Why Python as the first substrate?
1. **Iteration speed**: quick REPL cycles + cheap refactors.
2. **Tooling**: tests/lint/typecheck so future work is reproducible.
3. **Embedding prototype**: easy to explore host APIs (editor objects, keymaps) later.

## Key commitment
Micromax is not an afterthought: it is the **plugin/config/macro** system for the editor we eventually build.
So we bake in:
- namespace hygiene (wordlists + search order)
- safe host boundaries (allowlisted hostcalls)
- hard “won’t freeze host” rails (step budgets, later time budgets)
