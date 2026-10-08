# operationsfold audit/refactor

`operationsfold.py` is the rev0040 current-path audit.

It checks that these surfaces remain visible through code, tests, docs, `PUBLIC_SURFACE.json`, `HEAD_REGISTRY.json`, `docs/00-index.md`, `foldmap`, `foldregistry`, and `surfaceledger`:

```text
operatorintent
servicebreaker
serviceexit
operationsfold
```

It also preserves rev0039 `serviceopsfold` as predecessor history. This keeps the cube from hiding operational-control branch debris while it continues to grow.
