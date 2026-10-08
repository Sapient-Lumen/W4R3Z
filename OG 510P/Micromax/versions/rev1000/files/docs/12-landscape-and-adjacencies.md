# Landscape survey: Forth and its adjacencies

This document is the "ideas hunting ground". It’s intentionally opinionated.

## We are not chasing Forth-2012 compliance
Forth-2012 word sets (Core + optional sets) are a useful vocabulary for talking about features, but micromax can diverge freely.

Still, some traditional mechanisms solve real problems for an editor plugin ecosystem.

## Traditional Forth ideas we actively want

### 1) Wordlists + search order (namespaces without heavy machinery)
Forth’s Search-Order word set exists specifically to manage multiple word lists and control lookup order.

- Standard: https://forth-standard.org/standard/search
- `SET-ORDER` specification: https://forth-standard.org/standard/search/SET-ORDER

**Why it matters for an editor**: per-plugin wordlists and controlled shadowing prevent “global dictionary soup”.

### 2) Live system extension ("compiler is not sacred")
A recurring Forth theme is that you extend the language by defining words rather than editing a compiler.

One framing: Forth does not rely on a static grammar in the same way as many languages; it is designed to be extended from within.

- Discussion: https://softwareengineering.stackexchange.com/questions/370518/why-does-forths-flexibility-make-a-grammar-inappropriate-for-it

**For micromax**: we want this power, but we also want guardrails and debuggability.

### 3) Two-level story: user-level vs hacker-level
There’s a useful distinction between a Forth that’s merely a stack language vs a Forth where the inner system is modifiable.

- Eli Bendersky: https://eli.thegreenplace.net/2025/implementing-forth-in-go-and-c/

**For micromax**: start user-level (Python substrate), but keep a path to hacker-level.

## Forth things we should treat as “optional” or “suspect”

### 1) Invisible interpreter state and dual semantics
Classic Forth often has an interpreter state (immediate vs compiling) and “dual” words.

- A recent walkthrough describing the two interpreter states: https://blog.jacobvosmaer.nl/0049-revisiting-forth/
- “Compiling words” / dual behavior in a traditional tutorial: https://www.forth.com/starting-forth/11-forth-compiler-defining-words/

**Why this is suspect**: editor scripting benefits from *explicit* boundaries between runtime, compile-time, and host interop.

### 2) Global ambient variables (`STATE`, `BASE`, etc.)
Some systems rely on global variables that subtly change parsing/meaning.

**Micromax preference**: where possible, keep semantics explicit, local, and inspectable.

### 3) Stack-shuffle tax
“Stack gymnastics” are a real ergonomic complaint, especially in large code.

**Countermeasures**:
- quotations + combinators
- optional locals for readability
- data types that reduce shuttle (records, maps) when it’s worth it

## Adjacencies worth stealing from

### Factor (Forth-descended, modern ergonomics)
Factor leans on quotations and combinators, and adds tooling like stack-effect checking/inference.

- Factor paper: https://factorcode.org/littledan/dls.pdf
- Factor docs: quotations vs words metadata (words have source/module metadata):
  https://concatenative.org/wiki/view/Factor/FAQ/What%27s%20Factor%20like%3F
- Factor stack inference constraints around combinators:
  https://docs.factorcode.org/content/article-inference-combinators.html

**Steal for micromax**:
- first-class quotations are non-negotiable
- consider a lightweight stack-effect checker later (even partial is valuable)
- treat “word metadata” as a real feature (source spans, docstrings)

### Joy (purely functional concatenative cousin)
Joy’s core story is quotation + combinators as the main abstraction mechanism.

- Overview: https://hypercubed.github.io/joy/html/forth-joy.html
- FAQ: https://hypercubed.github.io/joy/html/faq.html

**Steal for micromax**:
- keep a small, crisp set of higher-order combinators
- make quotation execution explicit (`call`) and predictable

### RetroForth (explicitly “not traditional Forth”)
RetroForth is interesting because it *embraces* being pragmatic and pulls from multiple concatenative traditions.

- Retro overview (prefix-guided compiler; quotations/combinators; vocabularies): https://retroforth.org/

**Steal for micromax**:
- pragmatic “what makes it pleasant” bias
- vocabulary/module conventions
- potentially a lightweight literate source format (later)

### Embeddable scripting languages (non-concatenative, but great lessons)

Even if micromax stays concatenative, we can steal *embedding* wisdom from languages that were
explicitly designed for it.

#### Wren
Wren’s docs emphasize the embedding API as a first-class design constraint.

- Embedding docs: https://wren.io/embedding/

**Steal for micromax**:
- keep the host boundary small and intentional
- build “escape hatches” deliberately (capability allowlists)

#### Janet
Janet sits in a “small but usable” niche and documents embedding clearly.

- Janet for Mortals: https://janet.guide/all/
- Janet embedding: https://janet-lang.org/capi/embedding.html

**Steal for micromax**:
- prioritize good errors + small containers
- make the embedding story stable and boring

#### Neovim Lua (async patterns)
Neovim’s Lua story shows how editor plugins often evolve toward callback + coroutine patterns.

- Neovim Lua docs: https://neovim.io/doc/user/lua.html

**Steal for micromax**:
- keep concurrency host-owned
- provide explicit hook/callback points and do budgeting on callbacks

## Low-hanging fruit ideas (non-exotic, high ROI)

1) **Budgeted evaluation** (step limits) for plugin safety
   - already implemented in rev3

2) **Per-plugin wordlists + strict search order conventions**
   - plan: plugin wordlist searched first, then editor API wordlist(s), then core

3) **Stack-effect annotations and optional checker**
   - even without full inference, explicit annotations help documentation and tooling
   - inspiration: Factor’s stack checker/inference constraints (see above)

4) **Better source locations and traces everywhere**
   - required if the language is the plugin system



## Embedded Forth precedent (why “language as plugin system” is not fantasy)

### FreeBSD loader: multiple embedded interpreters
FreeBSD’s boot loader historically embeds multiple interpreters, including a Forth interpreter based on FICL.

- loader(8): https://man.freebsd.org/loader

**Steal for micromax**:
- a “safe subset” mode can coexist with a full language
- configuration may want fewer sharp edges than plugins

### FICL: a portable embeddable Forth
FICL (“Forth Inspired Command Language”) is explicitly positioned as an embeddable, portable Forth written in C.

- Paper: “Ficl, FORML, & object forth” (ACM DL): https://dl.acm.org/doi/10.1145/606666.606672


### RetroForth handbook (details matter)
RetroForth’s handbook is worth skimming because it gets into how quotations and combinators are used in practice.

- Handbook (epub): https://www.retroforth.com/Handbook-Latest.epub


## Locals and stack effects (ergonomics that scales)

### Gforth locals
Many practical Forth systems add locals to improve readability. Gforth documents locals syntax and motivation:

- Locals tutorial: https://gforth.org/manual/Local-Variables-Tutorial.html
- Locals overview: https://gforth.org/manual/Locals.html

**Steal for micromax**:
- allow locals as an ergonomic layer, while keeping the language fundamentally concatenative.

### Factor stack effects and checker
Factor’s docs show how stack effect notation is used both for documentation and (optionally) for consistency checking:

- Stack effect declarations: https://docs.factorcode.org/content/article-effects.html

**Steal for micromax**:
- keep stack effect comments as docstrings now
- later add a dev-mode checker that validates declared effects for common combinators
