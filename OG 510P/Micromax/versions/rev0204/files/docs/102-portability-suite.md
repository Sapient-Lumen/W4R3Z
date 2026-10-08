# Portability suite

Micromax now ships a tiny **JSON portability corpus** for the parts of the language we expect future Rust/WASM hosts to preserve exactly.

Artifacts:
- corpus: `portability/kernel_cases.json`
- runner: `src/micromax/portability_suite.py`
- CLI: `tools/mxportable.py`
- tests: `tests/test_portability_suite.py`

## Why this exists

The ordinary pytest suite is still the main test harness, but it is Python-shaped: it imports helpers, reaches into objects directly, and sometimes validates reference-only tooling behavior.

For portability work, that is heavier than necessary. A future host should be able to load a tiny data file, execute snippets, and compare stacks/errors to the Python reference VM.

## Corpus shape

Each case is a JSON object like:

```json
{
  "name": "int-add",
  "category": "kernel",
  "source": "1 2 +",
  "expect_stack": [3]
}
```

Or, for expected failures:

```json
{
  "name": "uncaught-stack-underflow",
  "category": "kernel",
  "source": "1 drop drop",
  "expect_error_contains": "Stack underflow"
}
```

The corpus intentionally stays small and data-only:
- source text
- category
- optional tags
- optional `host_features` seed list for host-boundary probes
- expected final stack **or** expected error substring
- broad but simple optional tags for sliceable bring-up work (`memory`, `locals`, `namespaces`, `combinators`, ...)
- enough namespace/search-order coverage to teach future hosts the difference between search order and compilation wordlist (for example `definitions` persistence and `set-current` not making a wordlist searchable by itself)
- no host-specific side effects
- no opaque runtime objects in expected values

The loader also now fails fast on:
- duplicate case names
- missing categories / source text
- malformed cases that specify both stack and error expectations (or neither)
- non-portable expected values

## Running it

From the repo root:

```bash
PYTHONPATH=src python tools/mxportable.py
```

You can also point the runner at another corpus file:

```bash
PYTHONPATH=src python tools/mxportable.py path/to/cases.json
```

And you can inspect or run targeted slices during bring-up work:

```bash
PYTHONPATH=src python tools/mxportable.py --list --category kernel
PYTHONPATH=src python tools/mxportable.py --tag namespaces
PYTHONPATH=src python tools/mxportable.py --name set-current-roundtrip --name map-keys-return-sorted-list
PYTHONPATH=src python tools/mxportable.py --name-contains recover
PYTHONPATH=src python tools/mxportable.py --tag memory --json
PYTHONPATH=src python tools/mxportable.py --tag memory --inventory
PYTHONPATH=src python tools/mxportable.py --tag memory --inventory --json
```

## What belongs here

Good corpus candidates:
- portable kernel words
- boot stdlib combinators we expect every serious host to ship
- stable error behavior that future hosts should mirror closely enough for tooling

The current corpus now covers not just kernel basics, but also a few real boot-stdlib/safety behaviors Micromax actually leans on: `0=`, successful and failing `catch`, `while`, `when`, return-stack basics, `execute`, `constant`, `variable`, list clone/pop isolation, `to-int`, `to-str`, map inspection/mutation (`m@` missing=>`0`, `m-del` missing=>no-op for existing pairs, `m-keys`, `m-items`, `m-del`, `m-merge`), locals shadowing plus session-local query/removal, wordlist/search-order lookup plus duplicate-name precedence both across wordlists and within one wordlist, `set-current`, `in`, `dict-version` bump/stability cases (including `find`, `get-order`, `get-current`, `host.api-version`, and `host.features` lookup-only stability), positive + missing `host.feature?`, including missing-`host.feature?` lookup-only `dict-version` stability, bare-VM and seeded `host.features` (including duplicate-seed deduplication while staying sorted), quotation combinators (`bi`, `dip`, `2dip`, `2keep`, `tri`), recovery/cleanup aliases (`try?`, `try`, `recover`, `ensure`, `finally`), and budget exhaustion observed through `catch`.

When you need machine-readable output during bring-up, `mxportable --json` now emits selected case records plus summary/result metadata instead of only human text. When you need a lighter-weight view of what a slice covers, `mxportable --inventory` / `--inventory --json` report matching categories, tags, and case names without the full case bodies. And when you need *precise* replay of one or two known behaviors, repeatable `--name` filters now avoid fuzzy substring matching entirely.

Bad corpus candidates:
- editor hostcalls
- filesystem / shell / clipboard integration
- debug-only object identity details
- anything whose result shape depends on Python internals

## Maintenance rule of thumb

When you add or change **portable** VM behavior:
1. update `docs/42-portability-ledger.md` if the contract changed
2. add focused pytest coverage
3. add or update a portability corpus case when the behavior is part of the portable kernel / boot stdlib


Recent additions: `dict-version-stable-across-host-feature-predicate` and `dict-version-stable-across-missing-host-feature-predicate` pin down that `host.feature?` stays lookup-only with respect to dictionary/search-order cache invalidation whether the feature is present or absent.


Recent additions: `map-fetch-missing-returns-zero` pins down that `m@` returns `0` for missing keys, matching the contract Micromax already documents and tests elsewhere.

Recent additions: `map-delete-missing-preserves-existing-pairs` pins down that `m-del` is a no-op for existing entries when the requested key is absent.

Recent additions: `map-keys-empty-map-returns-empty-list` pins down that `m-keys` returns `[]` for an empty map rather than a sentinel or error.



## rev200 follow-up

The corpus now also includes `map-items-empty-map-returns-empty-list`, pinning down that `m-items` on an empty map yields `[]` rather than a host-shaped null/zero sentinel.

Recent additions: `map-merge-empty-source-preserves-destination` pins down that `m-merge` is a no-op for existing destination pairs when the source map is empty.


Recent tiny corpus additions include empty-map edge cases such as `map-merge-empty-source-preserves-destination` and now `map-merge-empty-destination-adopts-source`, so future hosts can validate both sides of the merge contract from JSON alone.


Recent additions: `map-has-missing-key-is-false` pins down that `m?` returns `0` for an absent key rather than a host-shaped sentinel or error.


Recent additions: `map-store-overwrite-updates-value` pins down that `m!` overwrites an existing key's value rather than creating host-shaped duplicate entries.
