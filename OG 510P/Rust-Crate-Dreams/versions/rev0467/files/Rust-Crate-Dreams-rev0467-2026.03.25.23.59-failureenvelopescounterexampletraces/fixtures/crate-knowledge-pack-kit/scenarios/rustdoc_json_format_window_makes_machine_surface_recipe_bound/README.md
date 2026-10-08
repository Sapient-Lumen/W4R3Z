# Scenario: rustdoc JSON format window makes the machine surface recipe-bound

Problem:
A consumer downloaded rustdoc JSON and is about to treat the machine-readable surface as universally supported.

What this scenario proves:
Machine-surface claims need a build-surface receipt that records toolchain channel and rustdoc JSON format window.

Good outcome:
The bundle records the exact recipe and warns that another consumer may need manual review or a different parser window.
