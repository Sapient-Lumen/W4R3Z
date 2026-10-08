# Portability follow-up: five-item `pick` / `roll` stack-shuffle cases (rev242)

Rev242 extends the tiny `stack-shuffle` portability slice with two slightly deeper five-item cases:

- `pick-four-copies-fifth-item`
- `roll-four-rotates-five-items`

## Why this is worth pinning down

The earlier rev239/rev240/rev241 cases already covered the named Forth rationale equivalences plus one four-item general-indexing step:

- `0 pick` = `dup`
- `1 pick` = `over`
- `1 roll` = `swap`
- `2 roll` = `rot`
- `0 roll` = null op
- `2 pick` = copy the third item
- `3 pick` = copy the fourth item
- `3 roll` = rotate four items

Those are useful, but a hand port can still get the *general* indexing rule subtly wrong while passing the shallower cases. A five-item `4 pick` / `4 roll` slice is still tiny, still data-only, and better at catching wrong-end indexing or `u` vs `u+1` rotation mistakes in array-based implementations.

## Added cases

```json
{
  "name": "pick-four-copies-fifth-item",
  "category": "kernel",
  "tags": ["stack", "stack-shuffle", "core-ext"],
  "source": "10 20 30 40 50 4 pick",
  "expect_stack": [10, 20, 30, 40, 50, 10]
}

{
  "name": "roll-four-rotates-five-items",
  "category": "kernel",
  "tags": ["stack", "stack-shuffle", "core-ext"],
  "source": "10 20 30 40 50 4 roll",
  "expect_stack": [20, 30, 40, 50, 10]
}
```

## Practical payoff

These two cases keep the portability corpus tiny while making one more general indexing point explicit for future Python/Rust/WASM hosts. They are especially useful when a new host uses:

- array indexing from the wrong end of the stack
- `u` vs `u+1` rotation math
- iterative implementations that already pass the shallower named equivalences

## Focused checks

```bash
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle
pytest tests/test_portability_suite.py tests/test_vm_rev11.py
```
