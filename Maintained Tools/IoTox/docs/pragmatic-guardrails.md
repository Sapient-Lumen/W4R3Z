# Pragmatic guardrails

Status: practical counterweight to `docs/edge-of-hope.md`. Updated 2026-10-01.

IoTox has a big ideal. The practical repo must keep saying what the current
tree actually permits.

## Current practical use

Good fits today:

- learning and testing self-owned Tox device control;
- pairing machines and keeping friendship separate from authority;
- noncritical private Linux regular-file sync;
- important working copies when versioned recovery custody and a restore
  rehearsal already exist;
- owner-approved Ratox construction and testing;
- self-mode SSH-like control between machines the owner has deliberately
  admitted to the self domain;
- content-free diagnostics and support review.

Poor fits today:

- sole storage for irreplaceable originals;
- unsupported filesystem semantics such as symlinks, devices, sockets,
  ACL/xattr-dependent data, sparse layout, or case-folding portability;
- safety-critical physical control;
- SSH replacement for arbitrary remote exec, port forwarding, agent
  forwarding, or interoperability;
- anonymity claims from one successful route;
- production support claims from same-host or founding-machine evidence alone.

## Sync guardrails

IoTox sync can converge authorized peers. A backup lets the owner recover when
authorized convergence was the wrong human outcome.

Before a real working directory:

1. Run `iotox sync-doctor`.
2. Create a noncritical rehearsal namespace first.
3. Keep versioned recovery custody outside every IoTox writer's authority and
   outside normal IoTox sync write/delete/GC mutation.
4. Restore that backup somewhere separate and verify it.
5. Run `iotox readiness storage` and read the blocked lines.
6. Treat every conflict as preserved truth, not an error to delete.

Current storage science accepts same-host ext4/btrfs dishonest-storage and
production-prefix replay gates. IoTox deliberately does not try to certify
storage media, disk survival, host integrity, or filesystem-wide corruption
recovery; those belong to backups, storage, operating-system security, and
operator practice. Precious data still requires versioned recovery custody,
restore drills, and a recovery runbook because that is the sync-layer discipline
IoTox can honestly check.

## Terminal guardrails

Ratox is SSH-shaped, not SSH-compatible. It is a remote PTY over Tox with an
owner-bound profile.

Remember:

- `--mode self` selects the host and local controller by default, but it does
  not install profiles, bind peers, grant `interactive.terminal`, or enable
  sudo;
- the peer does not select executable, argv, environment, cwd, profile, sudo,
  or forwarding;
- sudo requires a distinct owner-approved profile and the host's own sudoers/
  PAM policy;
- route loss can detach and resume a live PTY, but daemon death does not
  preserve the PTY today;
- stale shell paths and missing rescue tools are product risks, not cosmetic
  warnings.

## Route guardrails

Native Tox, Tox/Tor, and Tox/I2P are separate route classes. A route label is
evidence scope.

Do not silently fall back from a requested privacy route to native. Do not turn
a successful Tor/I2P cell into an anonymity certificate. Route status should
name what carried work without leaking endpoints.

## Support guardrails

Content-free is not information-free. A support bundle may still correlate
configuration shape, activity class, feature state, and counters.

Always:

```sh
iotox support-bundle plan ./iotox.support
iotox support-bundle create ./iotox.support
iotox support-bundle inspect ./iotox.support
```

Never turn support bundles into raw log sweeps, path dumps, terminal
transcripts, or attestation claims.

## Public handoff guardrails

The seed repository datacube is for exact-state public review:

```sh
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --seed
```

It is not a stable/no-concern product claim, not a secret-bearing backup, and
not project authority. The ordinary Git repository and its signed/evidenced
release decisions remain authoritative. Use the richer conversation datacube
only when the recipient needs nested founding-cube provenance.

## Deployment guardrails

Generated config and service examples are not authority ceremonies.

`iotox init write-config` does not create RecallRoot ownership, grant peers,
install terminal profiles, enable sudo, certify backup readiness, or prove
route privacy. `config-lint` and `run-check` are necessary preflights, not
deployment review by themselves.

## Feature-selection guardrails

Prefer features that prevent common wrong actions:

- first-contact diagnosis;
- short quickstart;
- sync phase watch;
- emergency sync pause/freeze;
- stale terminal profile and rescue readiness;
- word fingerprints;
- recovery planning;
- mesh retirement.

Delay features that mainly make demos look powerful:

- remote-selected exec;
- hidden authority grants;
- remote-selected paths;
- general forwarding;
- automatic sudo;
- magic rollback;
- raw support logs;
- live-state completion that leaks names or paths.

The pragmatic rule is simple: shorten the safe path, not the proof.
