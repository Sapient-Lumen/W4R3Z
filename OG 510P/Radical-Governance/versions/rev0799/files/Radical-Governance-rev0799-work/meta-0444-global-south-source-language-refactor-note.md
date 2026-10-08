# Meta 0444 — Non-English / Global South source-language repair and matrix-lint refactor

This revision repairs the non-English / Global South official-source gap with a concrete applied packet rather than another abstract inclusion note. It uses Brazil CadÚnico / gov.br / Bolsa Família / LGPD / digital-government / AI-plan sources and India Aadhaar / DigiLocker / DPDP sources to test source language, translation status, publication state, currentness, identity and benefit consequences, local implementation, and remedy routes.

The maintenance change is deliberately small but important: common recent test matrices are now validated by lint from `tools/test_matrix_registry.py`, the same registry used by the build path. That means this revision adds `GLOBAL_SOUTH_SOURCE_TESTS.*` without adding another one-off builder or another copied validation tuple.

Deferred: the next substantive risk lane should be health-benefit or prescription-drug coverage transition, especially where payer changes, prior authorization, formularies, notices, appeals, emergency fills, and treatment continuity interact.
