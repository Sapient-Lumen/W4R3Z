# Structural audit rev0347

Rev0347 adds a live-intake quarantine and synthetic-retirement layer on top of rev0346. The package now has materialized quarantine folders for every must-capture packet, a live replacement gate, a synthetic retirement ledger, validator negative controls, and SQLite views that keep public context and synthetic payloads from closing readiness.

Key audit result: all 60 packets remain blocked from readiness claims. Twenty-four seeded synthetic packets remain dry-run artifacts only; thirty-six packets still have no payload. All sixty retain active loss caps until live/anonymized evidence is quarantined, checked, adjudicated, retested where needed, verified, and passed through the claim kernel.
