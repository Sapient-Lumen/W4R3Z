# tls_backends_compile_together_but_policy_picks_one

A crate can technically compile with both `rustls` and `native-tls` enabled, but the maintainer only wants to support one backend per scenario.

This fixture exists to force the pack to keep separate:

- **technical coexistence**,
- **official backend-choice policy**,
- and **recipe-backed guidance** for the preferred scenarios.

Expected outputs:
- `backend_choice_required` scenario class
- conflict classification showing the combo is buildable but not the recommended receiver-facing lane
- recipe manifests for the separate backend scenarios
