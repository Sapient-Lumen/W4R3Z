# Operator access as leases (SSH certificates + recorded sessions, no permanent keys)

Operator access is inevitable.
If the platform doesn’t provide a blessed path, teams invent shadow paths:
- static SSH keys checked into secrets managers
- “temporary” bastion accounts that become permanent
- long-lived VPN credentials with no receipts

DeriveBSD should treat operator access as a **high-power capability lane**:
**leased, scoped, auditable, and revocable**, with ergonomics good enough that static keys feel silly.

This doc focuses on the headless fleet case (SSH). Desktop/remote-assistance is handled separately (see `docs/291-remote-assistance-sessions-as-evidence.md`).

Product-shape default is now fixed in `docs/467-operator-access-posture-by-profile.md`: A keeps operator access JIT/role-shell-first, B keeps local user-presence admin as the default with remote shell admin exceptional, C keeps static-key compatibility adapter-shaped, and D forbids standing vendor/admin keys by default. The product-shaped recording/detail/export defaults for that lane now live in `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`: A/D keep output-only TTY trails routine for brokered remote or maintenance sessions, B keeps ordinary local admin metadata-first unless a remote/breakglass shell lane is used, and C keeps output-only brokered remote-admin trails preferred.

## Goals

- **No permanent user keys**: SSH access defaults to short-lived certificates.
- **Scoped authority**: login is separate from escalation; forced commands and role shells are first-class.
- **Timeboxed + revocable**: access is a lease registered with the lease registry.
- **Evidence by default**: every session has a typed envelope and (optionally) a TTY recording.
- **Lockout safety**: risky changes use confirmable change-sets and auto-revert.

## Prior art worth stealing

- OpenSSH user certificates: a practical, widely deployed “boring PKI” mechanism.
- Bastionless/JIT access systems (Teleport, smallstep): short-lived certs + audit trails.
- “Commit confirmed” patterns from network devices (avoid SSH self-brick).

## Model

### 1) Access broker (`derive-accessd`) is the authority boundary

A host (or cluster) component owns the dangerous pieces:

- accepts access requests (human or controller)
- evaluates policy and approvals (including separation-of-duties when required)
- issues **short-lived OpenSSH user certificates** signed by an **operator CA**
- starts/stops optional **TTY session recording** (lease-bound)
- registers the lease for immediate revoke (`docs/249-lease-registry-and-cross-lane-revocation.md`)

The broker is not “the SSH server”. It is a *policy gate* and *evidence producer*.

### 2) SSH certificate issuance (default)

DeriveBSD treats SSH CA roots as part of the explicit trust model:

- operator CA public key is distributed via `pki-trust-bundle` (intended_use = `ssh.user.ca`)
- the broker holds or portals access to the signing key (see `docs/306-crypto-operations-portal-and-split-keys.md`)

Certificate constraints should be used aggressively:

- **principals**: map to roles, not individuals (e.g. `ops-readonly`, `ops-breakglass`)
- short validity window (minutes)
- critical options (where supported):
  - source-address restriction
  - force-command for restricted roles
  - disable agent/X11/port forwarding by default
  - PTY permission as an explicit scope

### 3) SSHD integration (keep it boring)

A practical integration path on FreeBSD:

- `sshd` trusts the operator CA for user certs (derived config)
- session admission consults the broker for lease validity:
  - PAM module or `AuthorizedKeysCommand`-style hook
  - on allow, return “session knobs” (recording required, forced role shell, environment constraints)

The OS should make “broker in the loop” the default **without forking sshd**.

### 4) Role shells and escalation are distinct

Login should not imply root.

- “ops-readonly” lands in a restricted shell by default.
- escalation is a separate lane (policy + receipts), e.g.:
  - `doas`/sudo rules as derived artifacts (`docs/147-doas-minimal-privilege-escalation.md`)
  - breakglass grants for exceptional cases (`docs/236-breakglass-and-recovery-mode.md`)

### 5) Session recording is an attachable lease scope

Recording is valuable, but must not become ambient surveillance.

- default: **metadata-only** `operator.session` evidence
- optional: output-only TTY recording bound to the access lease
- input capture is a higher-risk scope requiring explicit policy

See: `docs/292-terminal-session-recording-as-evidence.md`.

### 6) Lockout safety: confirmable change-sets

Operator sessions often exist to apply risky changes (firewall, SSH policy, routing).
Those should use confirmable change-sets:

- apply into a candidate BE
- require confirmation within a timeout
- auto-revert on missing confirmation

See: `docs/242-confirmable-change-sets-and-auto-revert.md`.

## Evidence

### `operator.session` (new)

Every operator session should emit a typed envelope:

- who/what authenticated (principal + issuer)
- where from (remote addr)
- which lease(s) authorized it (`lease.envelope` digest references)
- which constraints were active (role shell / forced command / forwarding flags)
- pointers to recordings (if enabled)

Schema: `spec/operator.session.schema.json`
Example: `spec/examples/operator.session.json`

The official support handoff can now carry `operator_session_digests` on the typed bundle contract, so incident bundles do not have to reconstruct operator access from TTY recordings, ticket notes, or bastion dashboards.

### Budgets and drift

Operator access should be budgeted like any other authority:

- max concurrent sessions
- max sessions/day
- max recording bytes and retention
- default deny for port forwarding / agent forwarding

See: `docs/298-authority-budgets-and-permission-drift-alarms.md`.

## Open questions

- Where does the operator CA live by default: local HSM/TPM, KeyVM, or external KMS?
- How do we represent “role shells” cleanly (promise profiles vs a separate `ops.profile` vocabulary)?
- Which restricted roles still deserve stronger recording or retention than the new profile-shaped default?

Last updated: 2026-03-21r358
