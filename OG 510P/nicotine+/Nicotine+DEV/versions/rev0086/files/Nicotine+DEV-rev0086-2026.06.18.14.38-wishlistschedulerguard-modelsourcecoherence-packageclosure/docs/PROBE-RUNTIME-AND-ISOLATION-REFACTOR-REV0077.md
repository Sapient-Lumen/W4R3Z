# Search Again probe runtime and isolation refactor — rev0077

## Defect in the first harness design

The initial rev0077 probe launched one fresh Python/pytest process for every classified test. With 13 tests across two source states, that meant 26 interpreter startups before the two upstream-unit lanes. The evidence was valid, but the execution shape was wasteful and exceeded the available run window in this environment.

A second problem appeared in the upstream unit lane. Some Nicotine+ tests use multiprocessing. Capturing pytest through `stdout=PIPE` allows a descendant to inherit the pipe and keep the probe waiting even after the pytest parent has printed its final result. This is a harness lifecycle defect, not an upstream test failure.

## Refactor

Classified tests now run once per source state with JUnit output:

```text
classified pytest interpreters: 26 -> 2   (92.3% reduction)
all pytest interpreters:        28 -> 4   (85.7% reduction)
per-test expectation rows:      26 -> 26  (no evidence loss)
```

The JUnit parser reconstructs each test's pass/fail polarity and checks it against the declared state expectation. Aggregate pytest return code is not mistaken for failure, because two tests are intentionally red in each state.

Upstream units now write directly to a regular file under an isolated runtime directory. A bounded external process wrapper manages termination without relying on a captured pipe. HOME, XDG paths, TMPDIR, cwd, source extraction, and source state remain separate.

## Guardrails

The package audit requires:

- `run_state_tests()` and JUnit collection;
- absence of the old per-test `run_test()` process launcher;
- complete collection of 13 tests in each state;
- 26/26 expectation matches;
- a regular-file unit runner; and
- parity between baseline and selected upstream unit results.

## Result

```text
baseline classified state: 2 expected failures / 11 passes
selected classified state: 2 expected failures / 11 passes
expectation matrix:         26/26
baseline units:             60 passed / 1 skipped
selected units:             60 passed / 1 skipped
```

Elapsed times in packaged logs are normalized so repeated successful runs do not create meaningless artifact churn.
