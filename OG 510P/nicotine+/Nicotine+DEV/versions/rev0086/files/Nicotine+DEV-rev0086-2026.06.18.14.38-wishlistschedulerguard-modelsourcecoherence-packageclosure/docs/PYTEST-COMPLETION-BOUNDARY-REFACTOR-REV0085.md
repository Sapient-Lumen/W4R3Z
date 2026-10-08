# Pytest completion boundary refactor — rev0085

## Defect in the evidence harness

The interrupted rev0085 attempt exposed a distinction the older harness did not
model:

```text
JUnit is parseable != pytest lifecycle returned != Python process exited
```

Nicotine+ unit tests can leave non-daemon application threads alive after
pytest has completed. A normal Python interpreter can therefore wait during
shutdown even after pytest has printed its successful summary and finalized
JUnit XML.

An intermediate workaround watched for parseable JUnit and could force the
process to exit after a grace period. That bounded the hang, but it was not a
sufficient completion authority: a parseable report does not prove that
`pytest.main()` returned or that all pytest teardown hooks finished.

## Current boundary

`tools/run_pytest_completion_exit.py` now has one narrow contract:

1. invoke `pytest.main()`;
2. wait for that call to return;
3. atomically write and `fsync` a completion marker containing the exit code;
4. flush stdout and stderr;
5. call `os._exit(exit_code)` to bypass only leaked-thread interpreter shutdown.

It does not inspect progress text, poll JUnit, start a timer, or infer completion
from a session-finish hook. The parent runner requires all of the following:

```text
child return code == marker exit code == 0
marker says pytest_main_returned == true
JUnit exists, parses, matches its retained digest, and has expected outcomes
source extraction and HOME/XDG/TMP/CWD trees are removed
no runtime writes remain in the disposable source inventory
```

## Contract-driven unit lanes

One revision-neutral runner now owns both source modes and both states:

```text
bundled master baseline
bundled master cumulative candidate
exact public-head baseline
exact public-head cumulative candidate
```

The old rev0085-specific runner and the JUnit-watcher wrapper were removed.
`data/current_unit_lane_contract.json` binds the current runner and completion
wrapper by path and SHA-256.

The retained evidence audit reports:

```text
profiles:                    2
lanes:                       4
testcase records:          244
contract/evidence checks: 136/136
negative mutations:          6/6 rejected
```

This corrects a serious cube failure mode: successful test output can no longer
be silently promoted to a clean lifecycle result while the actual completion
boundary remains unknown.
