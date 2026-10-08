# anonsync_core rev0648

This C++20 library is a local authorization, replay-reservation, outbox, relay-recovery, and evidence kernel. The active service-shaped ingress boundary is explicit about which data is trusted and which data is attacker-controlled.

## Active boundary

- SQLite ledger schema: v10.
- Active backend capability format: exact v42; active manifest file is `gateway/rev0648-cpp-ledger-backend-capabilities.json`.
- Service config: `anonsync-ingress-service-config-v6-trusted-context-separated`.
- External request: `anonsync-ingress-reservation-request-v2-trusted-context-separated`.
- Trusted context: `anonsync-ingress-transport-context-v1`.
- Service report: `anonsync-ingress-reservation-report-v8-ledger-integrated-replay`.
- Sender material: `anonsync-ingress-sender-possession-v5-lp-rs256-trusted-context`.
- Replay cache: `anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction`.
- Relay report: `anonsync-sqlite-effect-relay-report-v3-handle-boundary`.
- Downstream store: `anonsync-relay-downstream-store-v2-provenance-bound`.

The public reservation API is:

```cpp
IngressReservationServiceResult reserve_ingress_request_json(
    const IngressReservationServiceHandle& operator_service_handle,
    const IngressTransportContext& trusted_transport_context,
    const std::string& request_json_text);
```

The handle carries only a service-config path and expected SHA-256. The implementation reloads and validates the operator config. The external request cannot carry trusted identity fields. The typed context must be constructed by a real transport/authentication adapter in a deployment; a caller-created local struct or CLI file is not itself authentication.

## Security hardening through rev0648

- bounded JSON integer access within the interoperable binary64 integer range;
- strict JSON whitespace and raw UTF-8 validation;
- unsigned Base64url decode accumulator and long-input regression coverage;
- canonical nonempty RSA Base64urlUInt values and minimum 2048-bit/112-bit key strength;
- request/context/config byte ceilings;
- fail-closed private-workspace permissions;
- service-path sender replay rows are inserted in the same SQLite/WAL transaction as the prepared ledger entry and outbox reservation;
- local downstream result rows bind adapter id, adapter kind, adapter config digest, config handle, and registry digest;
- local downstream stores use symlink-family rejection, `SQLITE_OPEN_NOFOLLOW` when available, WAL, and `synchronous=FULL` verification;
- relay transition signer/trust authority is preflighted before outbox claim or downstream touch.

The executables named `anonsync_fuzz_*` are deterministic parser/corpus regression launchers, not coverage-guided fuzzers. Their names remain for build compatibility; they must not be cited as fuzzing evidence.

## Known P0 seams

The remaining high-risk boundaries are outside this local cube: real TLS/mTLS/DPoP ingress, signed operator control plane, HSM/remote signer custody, a real downstream adapter with native idempotency/reconciliation, distributed replay authority, independent witnessing, and explicit privacy/retention semantics.
