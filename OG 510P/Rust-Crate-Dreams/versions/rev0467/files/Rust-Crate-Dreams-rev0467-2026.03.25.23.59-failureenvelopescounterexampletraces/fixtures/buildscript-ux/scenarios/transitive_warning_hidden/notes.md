# Scenario: transitive warning hidden

This scenario exists to prove that **P-0046** is not only about hard failures.

Cargo documents that build-script warnings are typically only shown for path dependencies, or more broadly when users opt into very verbose output. A useful report layer therefore needs a way to preserve *important but otherwise easy-to-miss warnings* in a support artifact.
