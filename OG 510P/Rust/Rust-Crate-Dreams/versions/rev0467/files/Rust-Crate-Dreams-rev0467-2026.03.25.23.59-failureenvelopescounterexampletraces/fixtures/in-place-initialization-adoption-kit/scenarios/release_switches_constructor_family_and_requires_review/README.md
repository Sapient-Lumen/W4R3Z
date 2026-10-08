# Scenario: release switches constructor family and requires review

A crate moves from a `pin-init`-based path to a local unsafe adapter or to a Crubit/`moveit` lane. Even if behavior still appears correct, this is meaningful contract drift.
