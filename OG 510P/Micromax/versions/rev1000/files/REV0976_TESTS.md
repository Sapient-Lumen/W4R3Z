# Revision 0976 tests

## Scope

This is a risk-targeted integration record, not a claim that the entire repository suite ran. It covers the two reconciled safety lines, their nearest VM/editor consumers, portability, generated contracts, repository structure, and reproducible publication.

## Focused union — 121 passed

A sealed-tree run passed **121/121** tests in **22.40 s**:

```text
tests/test_integer_domain.py
tests/test_regex_containment.py
tests/test_regex_hostcalls.py
tests/test_plugin_execution_budget.py
tests/test_effect_contracts.py
```

This lane exercises source and conversion bounds, transactional arithmetic, bytecode revalidation, plugin integer amplification, regex child memory/protocol behavior, hostcalls, and the generated effect/resource contract together.

## Adjacent compatibility — 184 passed

A sealed-tree run passed **184/184** tests in **12.47 s** across VM/core/bytecode/smoke behavior, string and hostcall result budgets, plugin surface/reload behavior, search, query-replace, replacement planning, and TUI search highlighting.

## Structure and publication — 68 passed

A sealed-tree run passed **68/68** tests in **29.46 s**:

```text
tests/test_revision_index.py
tests/test_docs_living_hygiene.py
tests/test_mxcontext.py
tests/test_mxaudit.py
tests/test_mkrevzip.py
```

The lane includes fixed-stamp byte reproducibility, provenance and lineage verification, duplicate-member rejection, mixed-generation source-snapshot rejection, revision-index checks, and bounded context generation. One expected `zipfile` warning is emitted by the deliberate duplicate-member rejection fixture.

## Portability and current-source checks

- `tools/mxportable.py --quiet`: **172/172 portability cases passed**.
- `tools/mxtimely.py`: context, audit, lint, portability, and doctor preflight all passed in **27.02 s**.
- `tools/mxaudit.py --check`: passed for rev0976.
- `tools/mxeffects.py --check-help-doc --check`: passed; **23** effect/resource rows and current installed help.
- `tools/mxcontext.py --json --check`: passed; rev **976**, **64** bounded documents, **58** code paths, no missing paths or revision warnings.
- `scripts/lint.sh`: `mxlint: ok`.
- `git diff --check`: passed.

## Final archive gate

The source tree is cleaned of caches and generated test artifacts before packaging. The final ZIP is accepted only after `mkrevzip.py --verify-archive`, independent ZIP integrity testing, filename/revision/tag checks, embedded-context checks, and a clean source snapshot all succeed against the final immutable commit.
