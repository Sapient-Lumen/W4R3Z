# Scenario: revoked device after key epoch

A shared-group workspace rotates to a new MLS-shaped epoch after removing a tablet that was reported lost.
The removed tablet later attempts to reconnect using stale bootstrap material.

This scenario exists to show that a worthy local-first kit should diagnose the failure as **membership drift / revoked device**, not generic sync flakiness.
