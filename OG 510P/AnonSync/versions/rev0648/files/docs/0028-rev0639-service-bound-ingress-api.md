# rev0639 service-bound ingress API

Rev0639 targets the next risky boundary after rev0638: the profile-bound ingress command prevented the request body from selecting ledger, controls, contracts, proof secret, capability pins, ledger mode, or policy envelope, but the active executable surface still accepted the operator profile path and profile digest on the same invocation as the request file.

The new forward path is a service-bound boundary:

- public C++ API: `reserve_ingress_request_json(const IngressReservationServiceConfig&, const std::string& request_json_text)`
- service config format: `anonsync-ingress-service-config-v1`
- service report format: `anonsync-ingress-reservation-report-v2-service-boundary`
- CLI harness: `--ingress-service-config`, `--ingress-service-config-sha256`, `--ingress-request`, `--ingress-report`

The service config is loaded and digest-pinned as operator boot material. It pins one ingress profile path and profile digest. The per-request API accepts request JSON text, not a request-side profile path, profile digest, ledger path, controls path, contracts path, backend capability path, proof secret, clock, backend mode, policy envelope, or ledger reset flag.

The profile-bound rev0638 command remains as an internal adapter/harness because it already centralizes sanitization and reservation generation. The rev0639 service report records this reuse with a hash of the legacy profile-command report and service-bound evidence stating that the public API accepted request JSON text rather than a request path/profile tuple.

## Fail-closed behavior added

The rev0639 validator checks that these cases fail before append:

- service config digest mismatch
- disabled service config
- ingress profile digest drift behind a still-pinned service config
- request operator-field injection
- request metadata ledger-mode selection
- v33 capability downgrade through the service-pinned profile
- accidental combination of service-config CLI and direct profile CLI arguments
- duplicate ingress replay after a prior durable reservation

## Refactor/audit note

The useful refactor this round is not a broad file split. It is a boundary split: callers can now use a reusable in-process API where the request arrives as data and the service carries operator configuration. The old file-oriented profile command is demoted to an internal adapter for that API. That cuts the riskiest request/operator mixing without spending the turn on registry expansion or source-file choreography.

The remaining structural waste is still real: `runner.cpp`, `reporting_selftests.cpp`, and `sqlite_replay_ledger.cpp` remain too large. The next cleanup should move ingress boundary code out of `runner.cpp` once the service boundary stabilizes.

## Residual risk

This is still not a deployed listener, TLS terminator, proof-of-possession system, HSM-backed control plane, independent witness, or distributed exactly-once protocol. The service config is digest-pinned local JSON, not signed authenticated configuration. The request still carries fixture HMAC proof material rather than sender-constrained DPoP/certificate-bound tokens. Real downstream unknown-outcome reconciliation remains the next high-risk product seam.
