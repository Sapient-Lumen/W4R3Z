# Stdlib package-resource trust (rev748)

Micromax's stdlib is written in Micromax (`src/micromax/stdlib/core.mx`) and loaded by the Python VM at startup.  Before rev748, the source tree had the file but the built wheel could omit it, because package data did not explicitly include `*.mx` resources.  That made installed-package startup weaker than source-tree startup: `VM()` could silently miss stdlib words such as `finally`, `recover`, and `2drop`.

Rev748 makes that boundary explicit.

## Guarantees

- Built wheels include `micromax/stdlib/core.mx` through setuptools package data.
- `VM()` still supports minimal embeddings by treating missing stdlib resources as non-fatal by default.
- Missing stdlib is no longer silent: the VM records `startup_diagnostics` and exposes `stdlib_health()` / `startup_health()`.
- Hosts that require installed-package semantics can construct `VM(strict_stdlib=True)` and fail closed if the resource is absent.
- A wheel/install smoke test builds the package, inspects the wheel archive, installs it into a temporary target, and checks that `VM(strict_stdlib=True)` sees stdlib words.

## Health shape

The stdlib health record is deliberately plain data:

```python
{
    "state": "loaded",          # loaded | missing | disabled
    "resource": "micromax/stdlib/core.mx",
    "loaded": True,
    "source": "<stdlib/core.mx>",
    "error": None,
}
```

When startup is degraded, diagnostics preserve the resource and the underlying exception text:

```python
{
    "kind": "missing-stdlib",
    "resource": "micromax/stdlib/core.mx",
    "message": "Micromax stdlib resource could not be loaded",
    "error": "FileNotFoundError: ...",
}
```

This keeps the default embedding contract flexible without making installed-package failures invisible.

## Tests

Focused coverage lives in:

- `tests/test_stdlib_startup.py`
- `tests/test_packaging_stdlib.py`
- `tools/mxdoctor.py::check_stdlib_resource`

The wheel smoke test is intentionally end-to-end because the bug lived outside ordinary source-tree imports.  It proves the artifact itself carries the Micromax stdlib resource.
