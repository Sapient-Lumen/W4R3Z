# ADR 0116: freeze one binding send and reciprocal record per worker epoch

Status: accepted

Date: 2026-08-21

## Decision

An auxiliary worker advertises route-binding-v1 only when its parent supplies both a sodium verifier
and a narrow binding-frame factory. The factory receives only the signed member policy, confirmed
session snapshot, and a supervisor-generated nonzero message identifier. This keeps arbitrary
stable-device signing outside the worker API.

After the canonical HELLO/CAPABILITIES transcript confirms, the worker invokes that factory once,
freezes the returned frame and message identifier, and retries only those exact bytes when transport
enqueue reports a retryable failure. Transport acceptance is recorded separately from reciprocal
authentication.

The receive side retains at most one exact route-binding frame per worker epoch. A different second
frame fails closed. If primary trust is not yet available, the bounded record waits without becoming
authenticated. Once trust exists, it enters the coordinator-owned registry from ADR 0115. Invalid
evidence is latched rather than cryptographically reverified on every 10 ms service cycle; replacing
primary trust permits one deliberate reevaluation. Disconnect discards both epoch-bound frames and
authentication facts.

## Consequences

Feature advertisement now means that a worker has a usable signing and verification path, not merely
that message type 19 has a decoder. Binding generation cannot consume unbounded randomness or signer
work during send pressure. Early auxiliary establishment does not race primary authority discovery,
and malicious invalid evidence cannot create a continuous signature-verification loop.

The Agent does not yet install the factory or populate live primary trust, so the shipped command
surface remains unadvertised and routes remain `connecting`. The next slice owns that final wiring
and coordinator lifecycle transition.
