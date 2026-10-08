# Scenario: missing accessible name in dialog

A confirm dialog renders two buttons.
One button has focus and an action, but no accessible name.

This scenario exists to prove that the doctor/gate surface can:

- classify the issue as blocking,
- attach the problem to one stable node id,
- and produce a CI-friendly gate failure without needing platform capture.
