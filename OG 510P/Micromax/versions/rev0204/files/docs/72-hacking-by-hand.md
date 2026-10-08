# Hacking Micromax by Hand (offline-friendly)

If you’re stuck without internet and without an LLM, you should still be able to evolve micromax.

The guiding idea: keep the core small, readable, and relentlessly tested.

## Repo map

### Language/VM

- `src/micromax/vm.py`
  - tokenizer
  - execution loop
  - locals frames + `.word` sugar
  - wordlists/search-order
  - budgets, errors

- `src/micromax/core.py`
  - core words (primitives)
  - file loading, modules, hooks
  - embedding contract helpers

### Editor (micro-esque target)

- `src/micromax_editor/editor.py` — headless editor core + actions
- `src/micromax_editor/buffer.py` — line buffer (swapable later)
- `src/micromax_editor/command_dispatcher.py` — command bar
- `plugins/` — micromax plugins (one wordlist per plugin)

### Tests

- `tests/` — add tests whenever you add a language or editor feature

## Run the basics

```bash
make test
make doctor
python -m micromax.repl
python -m micromax_editor
```

## Inspect tier-2 bytecode

If you are working on the compiler/bytecode layer, these helpers are useful:

```bash
# list words defined by a file
python tools/mxbytecode.py path/to/file.mf

# disassemble a word (compile if needed)
python tools/mxbytecode.py path/to/file.mf --word foo

# emit JSON (see docs/27-bytecode-serialization.md)
python tools/mxbytecode.py path/to/file.mf --word foo --json
```

## Local git (optional, but helpful)

If you want local history without GitHub:

```bash
make init-git
```

## How to add a primitive word

1) Add a Python function in `core.py`:

```python
def w_myword(vm: VM) -> None:
    ...
```

2) Register it near the bottom:

```python
vm.define_primitive("myword", w_myword, doc="...", wid=install_wid)
```

3) Add tests in `tests/`.

## How to add syntax sugar

Prefer the smallest possible changes:
- avoid complex parser state
- do sugar as a rewrite in the VM execution loop (like `.word` and `->name`)
- keep error spans accurate

## Conventions

New language/editor features must include:

- a short doc in `docs/`
- a decision entry in `docs/41-decisions-log.md`
- at least one test
