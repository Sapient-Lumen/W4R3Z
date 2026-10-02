# 0395 — Add evidence-gated stable release

Date: 2026-09-20

Status: accepted; sync custody terminology superseded by ADR 0405

## Context

`iotox ship-check stable` correctly failed closed, but the only stable answer
was hardcoded blocked. That protected the project from overclaiming, but it did
not define the exact path by which sync and Ratox could eventually graduate.

Stable/no-concern still depends on evidence outside the single development
workstation: versioned recovery custody, restore drills,
Ratox long soaks, route-loss evidence, sudo/PAM policy, security review, and an
explicit owner activation decision.

## Decision

Add an evidence manifest path to the native gate:

```sh
iotox ship-check [sync|terminal|all] stable \
  --evidence-manifest stable-evidence.manifest
```

The manifest is bounded `key=value` text with schema
`iotox.stable-evidence.v1`. Every required gate must have:

```text
gate=accepted
gate.receipt-path=relative/or/absolute/path
gate.receipt-sha256=<64 lowercase hex>
```

Relative paths resolve from the manifest directory. The binary opens every
receipt as one bounded no-follow regular file and verifies the listed SHA-256.

The sync stable scope requires:

- `sync.local-preflight`;
- `sync.storage-readiness`;
- `sync.recovery-custody`;
- `sync.restore-drill`; and
- `sync.recovery-runbook`.

The Ratox stable scope requires:

- `terminal.daily-control`;
- `terminal.profile-freshness`;
- `terminal.service-supervision`;
- `terminal.reconnect-continuity`;
- `terminal.cgroup-delegation`;
- `terminal.route-loss`;
- `terminal.long-soak`;
- `terminal.tor-route-loss`;
- `terminal.i2p-route-loss`;
- `terminal.sudo-policy`;
- `terminal.security-review`; and
- `terminal.activation-decision`.

Without a manifest, stable remains blocked. With an incomplete or malformed
manifest, stable remains blocked and prints one `stable-evidence-blocker` per
missing or invalid gate. With a complete manifest for the selected scope,
`ship-check stable` may return success and report `stable-without-concern=accepted`.

Add `tools/iotox-repo.sh stable-evidence-plan` and require
`tools/iotox-repo.sh release-check stable --evidence-manifest PATH` for stable
release checks.

## Consequences

Stable is no longer impossible by hardcode, but it is still not achieved in the
repository by default. The mechanism binds claims to content-free receipt or
review-record files and hashes; it does not make those receipts trustworthy by
itself. Release owners must verify the receipt set and keep it with release
notes or support evidence.

Founder-preview semantics are unchanged.

## Validation

The human CLI process test now verifies:

- stable without a manifest remains blocked;
- an incomplete manifest remains blocked and names missing gates; and
- receipt hash mismatch remains blocked; and
- a complete manifest backed by receipt files can graduate the selected stable
  scope.

`tools/iotox-repo.sh stable-evidence-plan` is covered by a CTest smoke.
