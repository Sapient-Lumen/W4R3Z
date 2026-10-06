# ADR-0057: Operator-access posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has a credible **operator-access lane** on paper:
`docs/311-operator-access-leases-and-ssh-certs.md` treats operator sessions as leased, certificate-based, and auditable,
`docs/292-terminal-session-recording-as-evidence.md` narrows recording posture,
`docs/236-breakglass-and-recovery-mode.md` keeps emergency access explicit,
and the recent A–D profile work already fixes remote assistance, private-key handling, human identity, data-at-rest, and export defaults.

What the archive still lacked was the **product-shape default** for human administrative access.
Without that, different deployments quietly normalize incompatible and risky habits:

- A quietly keeps permanent SSH keys or bastion accounts because "ops needs access".
- B cannot tell whether remote shell administration should be normal, exceptional, or absent in favor of local presence + remote assistance.
- C cannot tell whether static `authorized_keys` compatibility is an accepted default or only an adapter-shaped fallback.
- D risks production or factory images carrying standing vendor/admin credentials because maintenance access was never bounded as a product decision.

We do **not** need to choose one access broker, one CA backend, or one TTY-recording product here.
We do need a stable, checkable answer to:

- whether operator/admin access is local-first or remote-first by profile,
- whether standing keys/accounts are acceptable defaults,
- where short-lived certificates / leases / role shells are the default rather than an optional footnote,
- and when breakglass, quorum, or maintenance-window posture is required.

## Decision

We define operator-access posture as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under the stable `operator_access` knob.

Cross-profile guardrail:
- standing operator/admin SSH keys or permanent bastion accounts are **not** the preferred default in any profile,
- login is distinct from escalation; privileged shell/elevation is a separate reviewable lane,
- remote admin authority, when it exists, must land in leases/certs/policy rather than silent standing credentials,
- and operator session evidence remains mandatory even when full TTY recording is not.

### A) `fleet_host`

Default posture: `brokered-jit-cert-role-shell-escalation-separate`

- Fleet hosts use brokered, short-lived certificate-based operator access by default.
- Restricted role shells / forced-command posture is preferred over landing everyone in an unrestricted shell.
- Escalation is a separate lane from login.
- Standing SSH keys and permanent bastions are out of bounds as the normal access story.

### B) `workstation`

Default posture: `local-user-presence-preferred-jit-remote-admin-exceptional`

- Local admin/elevation should prefer secure-attention / user-presence mediated flows.
- Remote shell administration is exceptional rather than a standing workstation default.
- If remote admin exists, it must be explicit, leased/JIT, and reviewable.
- This decision does not replace the separate remote-assistance lane for visible user-mediated support.

### C) `general_os`

Default posture: `local-admin-default-jit-remote-preferred-explicit-static-key-adapter`

- Classic local admin remains the broad-compat default.
- JIT/leased remote admin is preferred when Derive-managed lanes are used.
- Static `authorized_keys` style access may exist only as an explicit compatibility adapter, not as the archive’s preferred posture.

### D) `appliance_factory`

Default posture: `maintenance-window-jit-cert-quorum-no-standing-admin-keys`

- Production/factory admin access should be maintenance-window-shaped.
- Standing admin/vendor keys in shipped or factory images are forbidden by default.
- JIT certificate access and stronger approvals/quorum remain the baseline for sensitive maintenance lanes.
- Breakglass remains explicit and separate rather than normalizing always-there backdoors.

## Consequences

- Product profiles now carry a stable `operator_access` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward permanent SSH keys, standing workstation remote admin, or factory/vendor backdoors.
- Risk item 39 narrows from a product-default question to implementation detail: offline broker reachability, role-shell vocabulary, recording defaults, workstation local elevation ergonomics, and renewal/revoke behavior.

## Non-goals

- Choosing one CA/HSM/KMS product or one access broker implementation.
- Freezing the exact recording scope, retention, or replay UI.
- Defining every role-shell profile, forced-command shape, or PAM hook here.
