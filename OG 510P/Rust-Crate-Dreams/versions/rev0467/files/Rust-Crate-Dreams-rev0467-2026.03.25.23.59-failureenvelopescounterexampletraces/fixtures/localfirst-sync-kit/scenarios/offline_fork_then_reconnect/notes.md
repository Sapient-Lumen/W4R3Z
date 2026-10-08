# Scenario: offline fork then reconnect

One user edits the same document on a laptop and a phone while offline.
Later the laptop reconnects over an iroh-based transport and completes a clean, ordered sync.

This scenario exists to show the happy path for `single_user_multi_device@1` without pretending that bootstrap details or relay fallback are irrelevant.
