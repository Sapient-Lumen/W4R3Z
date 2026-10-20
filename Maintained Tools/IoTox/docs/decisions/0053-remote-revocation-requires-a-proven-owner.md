# ADR 0053 — remote revocation requires a proven owner

Status: accepted and implemented
Date: 2026-08-14

## Context

ADR 0052 permits a recalled owner to grant the connected controller's stable device key a bounded
non-owner role. The same controller must later be removable without physical access to the target
device, but remote administration must not become a generic arbitrary-ledger-write API.

After enrollment, the controller's ordinary device proof is valid. An explicit owner ceremony must
therefore be able to prove the recalled owner without weakening the frozen proof rule into
unbounded claimant switching.

## Decision

One confirmed authority round admits at most two distinct valid claimant candidates:

- an unknown or revoked ordinary device may be replaced once by an explicit recovery claimant;
- an authorized non-owner device may be replaced once only by an active owner;
- an authorized owner is frozen, a third candidate conflicts, and any invalid replacement closes
  authorization for that round.

Remote revocation reuses the exact signed authority-record transport and correlated result from ADR
0052. The client reconstructs the target device's owner, the daemon prepares public body fields from
the peer's frozen challenge, and the client signs locally. The receiver accepts only a record that:

- is issued by the currently proven owner and targets the challenged device and exact ledger head;
- is a canonical `revoke` with role `none` and zero capabilities;
- names an existing active non-owner principal;
- passes the normal `AuthorityLedger` signature, sequence, continuity, and policy checks.

Owner revocation is deliberately excluded. Ownership succession remains the existing explicit
grant-new-owner then revoke-old-owner constitutional sequence and is not folded into ordinary
remote revocation.

Exact replay of the current signed revocation tail is idempotent and returns `exact-duplicate`
without requiring the now-invalidated prior owner proof. Any non-identical stale mutation fails
closed.

## Secret and authority boundaries

The RecallRoot phrase and derived owner secret remain only in the short-lived CLI process. The
controller daemon receives a public owner key and final signed record. Tox friendship, transport
queue acceptance, and a delegated `manage.principals` capability cannot substitute for the explicit
owner proof required by this ceremony.

## Evidence gates

- deterministic denial of owner, missing, inactive, and unauthorized revocation subjects;
- one applied revocation and byte-identical duplicate without sequence movement;
- authorized delegated-controller proof upgraded only to an owner proof;
- genuine remote revocation, receiver restart with the subject still inactive, recalled-owner
  re-entry, and explicit re-delegation;
- the same lifecycle in normal native and TCP-only modes.
