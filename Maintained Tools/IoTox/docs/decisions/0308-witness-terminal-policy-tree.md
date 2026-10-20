# ADR 0308: Witness the complete Ratox terminal policy tree

- Status: accepted and implemented for the opt-in terminal-policy lane
- Date: 2026-09-02

## Context

Ratox deliberately makes privilege escalation an owner-reviewed local policy. Profiles freeze the
executable, arguments, account, confinement, resource envelope, optional executable digests, and
whether host-authorized set-ID/file-capability helpers such as sudo may work. Principal bindings
select exactly one of those profiles. The store is strict, owner-private, descriptor-walked, and
canonical, but restoring an older complete `profiles/` plus `bindings/` tree can still resurrect a
previously permitted sudo shell or weaker confinement after the owner has removed it.

The store has no natural generation field and its offline administration commands update one
record at a time. Automatically accepting whatever valid tree is present at Agent startup would
turn filesystem rollback into authorization.

## Decision

Add a separately enrolled `terminal-policy` witness lane and a reusable low-churn policy-witness
transaction. The terminal subsystem computes one canonical semantic digest over the complete
validated profile/binding tree. It sorts by profile ID and principal, normalizes historical profile
records through the current v7 encoder, length-binds every record, and includes no path or ownership
metadata.

`iotox witness-terminal-policy-enrollment --config PATH` reads the reviewed tree and produces the
device-signed no-replace service enrollment. It changes neither local nor remote state. An absent
local checkpoint enrolls position one; an existing signed checkpoint is accepted only when its lane
and digest already match the reviewed tree.

Later offline profile installs/removals/binds/unbinds intentionally leave the tree uncommitted.
`iotox witness-terminal-policy-commit --config PATH` is the explicit review boundary. It:

1. strictly reloads and validates the complete store and computes its canonical digest;
2. writes and fsyncs a device-signed intent containing current/next heads, nonce, lane, and the exact
   next signed local checkpoint;
3. performs authenticated external committed-to-pending CAS;
4. atomically installs and re-reads the exact local checkpoint;
5. performs pending-to-committed CAS and fsync-unlinks the intent; and
6. reloads the policy tree and refuses success if it changed during the transaction.

Positions advance exactly once. An unchanged commit only reconciles and verifies. Ambiguous CAS
replies are resolved by authenticated query. Startup may finish a transaction only when its exact
device-signed intent already exists; it never creates a transition for a newly observed digest.
Missing pending intent, foreign selector, unrelated policy, forked/newer local checkpoint, service
outage, or wrong service key fails closed.

With `--witness-terminal-policy`, security initialization verifies the complete tree before
advancing the application or Ratox startup incarnations and before RuntimeTree. The exact verified
`ProfileStoreData` is cached and later installed into the live registry, so a subsequent disk edit
cannot change policy for that process. The default checkpoint derives as
`PROFILE_ROOT.witness-checkpoint`; its intent derives beside it. Both may be selected explicitly and
are part of the protected-state closure.

## Consequences

Five owned checks bring the direct registry to 781. They cover canonical semantic tree commitment,
explicit-commit-only advancement, complete local rollback, intent-before-CAS recovery, pending
recovery, same-domain refusal, and the actual authenticated TCP service.

The retained two-guest gate begins with a reviewed sudo-capable UID-1000 shell, enrolls policy one,
and successfully starts the Agent. It replaces that profile with a no-escalation profile and proves
startup refusal before runtime until the explicit commit command advances policy two. It then
restores both the old sudo-capable profile and its matching signed checkpoint while the service
stays at two and again requires refusal before RuntimeTree.

This lane protects profile and binding freshness only. It does not validate sudoers/PAM, establish
witness independence, protect profile executable bytes without profile-v7 digest pins, or make a
running host safe from root/kernel compromise. Sync, update, and mutating-command effects still need
their own transaction boundaries.
