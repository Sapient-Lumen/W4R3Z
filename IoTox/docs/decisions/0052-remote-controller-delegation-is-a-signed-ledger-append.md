# ADR 0052 — remote controller delegation is a signed ledger append

Status: accepted and implemented
Date: 2026-08-14

## Context

RecallRoot already reconstructs the stable owner signing key, and an explicit transcript-bound
authority proof can authenticate that owner over a confirmed peer session. Local owner ceremonies
can bootstrap, grant, and revoke ledger principals. The missing re-entry step is allowing a newly
installed controller to become an ordinary delegated principal without physically operating the
device's Unix socket.

Treating proof alone as a permanent grant would collapse session authentication into durable
authority. Letting the device manufacture an owner-signed record would require the device to know
the recalled secret. Neither is acceptable.

## Decision

Remote self-delegation uses one exact authority-record body and signature:

```text
fresh controller establishes and confirms an IoTox session
device challenges against its exact authority head
controller reconstructs RecallRoot owner and sends explicit owner proof
controller constructs the exact next grant body from the challenged head
controller signs that body locally with the recalled owner key
controller sends the complete 256-byte authority record
device checks session, proven owner, connected controller, and exact ledger head
device appends through the existing AuthorityLedger validator
all authority sessions invalidate and must prove again against the new head
```

The first remote ceremony is deliberately self-delegation. The record must:

- target the verifier device named by the current challenge;
- name the currently proven remote owner as issuer;
- name the connected peer's stable device principal as subject;
- be a `grant` for a non-owner role within that role's capability ceiling;
- use the challenged ownership epoch, next sequence, and exact tail digest;
- carry a valid owner signature and pass normal ledger replay policy.

The transport frame is only delivery. It does not authorize the mutation, and local send-queue
acceptance is not completion. The receiver returns a correlated result and projects the resulting
ledger generation. Exact duplicate delivery is idempotent only when its record digest equals the
current ledger tail; conflicting sequence reuse fails closed.

## Secret boundary

The RecallRoot phrase, root, owner seed, and secret key remain inside the short-lived controller CLI
process. Neither controller daemon nor device daemon receives them. The controller daemon may
prepare public body fields from its frozen peer challenge and transport the final signed record.

## Ownership changes excluded

This ceremony cannot grant `owner`, transfer ownership, revoke the last owner, advance the ownership
epoch, or recover from phrase compromise. Those require separately named ceremonies with stronger
operator warnings and rollback policy. ADR 0054 later defines that separate successor-possession
ceremony. IoTox retains no vendor reassignment key.

## Evidence gates

- exact codec and malformed/replay tests;
- denial before recalled-owner proof;
- denial when subject differs from the connected stable controller;
- successful separate-process self-delegation and fresh proof under the delegated key;
- duplicate replay without a second ledger record;
- device and controller restart with identical ledger truth;
- genuine-peer re-entry using a disposable phrase and controller.
