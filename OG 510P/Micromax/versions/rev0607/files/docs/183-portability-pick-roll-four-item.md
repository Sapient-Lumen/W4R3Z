# Portability follow-up: deeper `pick` / `roll` stack-shuffle cases (rev241)

Rev241 extends the tiny `stack-shuffle` portability slice with two slightly deeper four-item cases:

- `pick-three-copies-fourth-item`
- `roll-three-rotates-four-items`

## Why this is worth pinning down

The earlier rev239/rev240 cases already covered the named Forth rationale equivalences and the smallest zero/non-zero indexing edges:

- `0 pick` = `dup`
- `1 pick` = `over`
- `1 roll` = `swap`
- `2 roll` = `rot`
- `0 roll` = null op
- `2 pick` = copy the third item

Those are helpful, but a hand port can still get the *general* indexing rule subtly wrong while passing the shallow cases. A four-item `3 pick` / `3 roll` slice is still tiny, still data-only, and much better at catching off-by-one indexing mistakes in loop/array-based implementations.

## Added cases

```json
{
  "name": "pick-three-copies-fourth-item",
  "category": "kernel",
  "tags": ["stack", "stack-shuffle", "core-ext"],
  "source": "10 20 30 40 3 pick",
  "expect_stack": [10, 20, 30, 40, 10]
}

{
  "name": "roll-three-rotates-four-items",
  "category": "kernel",
  "tags": ["stack", "stack-shuffle", "core-ext"],
  "source": "10 20 30 40 3 roll",
  "expect_stack": [20, 30, 40, 10]
}
```

## Practical payoff

These two cases keep the portability corpus tiny while making one more general indexing point explicit for future Python/Rust/WASM hosts. They are especially useful when a new host uses:

- array indexing from the wrong end of the stack
- `u` vs `u+1` rotation math
- recursive/loop-based implementations that already pass the named shallow equivalences

## Focused checks

```bash
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle
pytest tests/test_portability_suite.py tests/test_vm_rev11.py
```
