# Probe source and process isolation refactor — rev0081

## Scheduling-dependent source defect

HOME, XDG, temporary-directory, and working-directory isolation did not make source lanes independent. Upstream tests can create fixture state inside their checkout. During development, a transient test file appeared in a source tree while another lane was measuring patch scope, creating a false fourth changed file.

## Correction

Every mutable upstream-unit lane now receives:

```text
one content-validated source extraction
candidate patch applied only inside the patched extraction
an external disposable HOME/XDG/TMP/CWD tree
lane-local JUnit and regular-file logs
JSON evidence bound to source digest, source ref, patch digest, and JUnit digest
source and process-environment cleanup before the result is accepted
```

The lightweight final probe independently extracts baseline and patched templates, gives the native core/network lane its own clone, verifies the prevalidated unit records, and removes all temporary source states.

## Completed-pytest shutdown defect

Some runtime threads can keep Python alive after pytest has emitted a complete result and JUnit. `tools/run_pytest_forced_exit.py` calls `pytest.main()`, flushes output, and terminates only after pytest returns. This prevents a wrapper timeout from relabeling a completed suite as a test timeout.

## Durable evidence boundary

Mutable HOME/XDG/TMP/CWD content is never package evidence. It is reduced to a path/kind/digest ledger, then deleted. Only JUnit, regular logs, and the cleanup ledger remain. Package validation independently rejects any transient environment or source-state directory under the current revision runtime-evidence root, without rewriting historical evidence.
