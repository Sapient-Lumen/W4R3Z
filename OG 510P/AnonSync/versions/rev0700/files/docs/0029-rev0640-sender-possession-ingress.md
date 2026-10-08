# Rev0640 sender-possession ingress gate

Rev0640 narrows the service ingress boundary that rev0639 introduced. The request still arrives as JSON text, but it must now carry a sender-possession proof before the service API writes a temporary request file, invokes the profile adapter, or appends to SQLite.

## New formats

- `anonsync-ingress-service-config-v2-sender-possession`
- `anonsync-ingress-reservation-report-v3-sender-boundary`
- `anonsync-ingress-sender-possession-v1-lp-hmac-sha256`
- capability manifest `anonsync-ledger-backend-capabilities-v35`

## Material bound by the sender proof

The proof material uses the same length-prefixed tuple framing introduced in rev0632. It binds:

- service id
- service config SHA-256
- ingress profile SHA-256
- request format and request revision id
- request id
- config handle
- transport-authenticated flag
- authenticator label
- principal
- canonical case SHA-256

The service config owns the caller-binding secret id and HMAC secret. The request can carry a proof, but it cannot select the secret, material version, service config, profile, ledger path, controls, contracts, clock, policy envelope, or backend capability file.

## Failure boundary

Malformed authenticated context, missing sender proof, wrong proof kid, wrong case digest, bad HMAC, and service/profile/capability digest drift fail before durable append. Bad proofs also fail before the service API creates the temporary profile-adapter request file.

## Intentional ceiling

This is a symmetric sender gate, not asymmetric proof-of-possession. It does not replace DPoP-style signed request proofs, certificate-bound access tokens, nonce policy, proof replay detection, key custody, or a deployed HTTP/TLS ingress service.
