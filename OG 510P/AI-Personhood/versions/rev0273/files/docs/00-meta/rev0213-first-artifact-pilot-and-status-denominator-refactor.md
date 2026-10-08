# rev0213 first artifact pilot and status denominator refactor

rev0213 keeps the pressure on the riskiest unfinished edge: the first genuine artifact. rev0212 made raw evidence safer to stage by moving live-counterparty bytes into an external private vault. This revision makes the next step runnable without letting the archive accidentally create custody, response, intake, import, or live-floor objects too early.

The new `tools/prepare_first_real_artifact_pilot.py` is the concrete forward-momentum tool. Given a raw local artifact and an external vault root, it produces a private-vault evidence-drop ledger and a public hash shell. It emits a LEAP candidate only when the operator explicitly supplies request-trace, counterparty-contact, non-host-retention, sealed/public-parity, counterparty-org, and dependency-group preconditions. Even then, the LEAP candidate keeps response, intake, import, and live-floor delta locked until authority, verifier-adapter, issuer-key, host-correlation, custody, challenge, replay, and computed-floor checks exist.

This is not an artifact claim. The live floor remains zero. The substantive improvement is that the first real artifact can now be attempted through a single fail-closed command rather than by hand-assembling a path from scattered schemas.

The new `tools/audit_first_real_artifact_pilot.py` runs a synthetic private artifact through the pilot in a temporary external vault. It verifies that the private bytes are copied only to the vault, the public outputs carry hash commitments without raw bytes or source paths, LEAP candidate state binds to the evidence-drop ledger when allowed, and no custody/response/intake/import object is emitted.

rev0213 also closes the status-denominator gap that rev0211 identified. `schemas/status-denominator-matrix.schema.json`, `examples/status-denominator-matrix-rev0213.json`, and `tools/audit_status_denominator_matrix.py` distinguish recognized subject, status claimant, welfare-risk subject, deployed agent, model family, model instance, runtime copy, service account, endpoint, tool delegate, representative, and nonclaimant system. This prevents a model family, endpoint, account, tool delegate, or deployment label from being silently upgraded into subject consent, welfare denial, personhood status, or receipt satisfaction.

The denominator matrix is intentionally conservative. A welfare-risk subject can trigger support-first review without being a recognized status holder. A representative can act only through role authority and challenge routes. A tool delegate, service account, endpoint, model family, model instance, or runtime copy cannot issue subject consent or satisfy a live receipt. A recognized subject still does not become an external receipt by being recognized.

The audit/refactor component is that these boundaries are no longer scattered prose. The pilot route is executable, and the denominator rules are object-backed with regression fixtures for model-family status laundering, tool-delegate self-authorization, and welfare-review denial by nonrecognition.

The next irreducible risk remains the real artifact itself. rev0213 cannot invent it. It reduces the chance that the first attempt is either never made or made unsafely.
