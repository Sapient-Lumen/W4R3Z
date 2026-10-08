# Pytest completion attestation — rev0085

## Failure mode

A parseable JUnit file and a terminal line saying that tests passed are not
proof that the test runner returned control. Nicotine+ unit tests can leave
runtime threads alive, so normal Python interpreter shutdown may wait after
`pytest.main()` has already finalized output.

The interrupted rev0085 attempt exposed the opposite cube error too: a wrapper
could time out after complete test output and still leave process lifecycle
ambiguous.

## Current contract

`tools/run_pytest_completion_exit.py` calls `pytest.main()` directly. Only
after that function returns does it atomically write:

```json
{
  "version": 1,
  "pytest_main_returned": true,
  "exit_code": 0
}
```

It flushes standard streams and uses `os._exit()` to bypass leaked-thread
shutdown. The parent runner independently requires all of the following:

- a matching process return code;
- a complete, parseable JUnit report with the declared testcase count;
- the atomic completion marker and its digest;
- zero failed/error testcases;
- exact candidate path, ID, and digest in the patched lane;
- a disposable source extraction;
- bounded HOME/XDG/TMP/CWD state and successful cleanup;
- an empty final source-write inventory.

This does not hide a test that never returns: no marker is written until
`pytest.main()` itself returns. It only separates pytest completion from
unrelated interpreter-shutdown thread leakage.

## Result

Four current lanes now use the same data-driven runner: bundled proxy baseline,
bundled proxy candidate, exact public-head baseline, and exact public-head
candidate. All four are bound to the current source and candidate contracts.
