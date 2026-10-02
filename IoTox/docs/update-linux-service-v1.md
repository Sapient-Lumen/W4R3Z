# Linux service deployment adapter v1

Status: implemented and dual-carrier VM-qualified construction adapter; physical-target
qualification remains open.

linux-service-v1 is the first named consumer of an IoTox update slot. It is intentionally a narrow
Linux service contract, not a package manager, archive extractor, bootloader, container runtime, or
arbitrary command surface. A release signer authorizes one native executable image for one exact
update-policy target. Synchronization and remote update.stage can make those bytes an inert
candidate; only owner-local update-apply, a later durable Agent incarnation, successful adapter
readiness, and the one-use health token can confirm it.

## Author and run a service policy

Executable intent is explicit in update policy v3. A positive signer-policy epoch is mandatory:

    iotox update-policy-template service-image iotox-linux-service-x86_64 \
      /var/lib/iotox/update \
      --signer-policy-epoch 1 \
      --payload-kind linux-service-v1 \
      RELEASE_PUBLIC_KEY_HEX > update.policy.new
    chmod 0600 update.policy.new
    iotox update-policy-lint update.policy.new

update-bundle-create reads the payload kind from that policy and signs it into the existing
fixed-size manifest. The payload must be a native Linux executable suitable for the target ABI.
Scripts are outside v1: the sealed image descriptor is close-on-exec and an interpreter pathname is
not an admitted second artifact.

    iotox --identity /secure/offline/release.identity \
      update-bundle-create update.policy.new service.elf service.iub \
      42 42.0.0

The Agent requires explicit activation of both the update lifecycle and the matching adapter. The
helper must resolve to the exact IoTox executable, not a mutable or unresolved symlink:

    IOTOX_BIN=/absolute/resolved/path/to/iotox
    "$IOTOX_BIN" run \
      --enable-sync \
      --sync-policy-root /etc/iotox/sync \
      --enable-signed-updates \
      --update-policy /etc/iotox/update.policy \
      --enable-update-linux-service \
      --update-service-helper "$IOTOX_BIN" \
      ...the ordinary identity, authority, state, runtime, and network options...

An opaque v1/v2 policy and --enable-update-linux-service fail closed. A v3 service policy without
the activation flag also fails closed. Thus changing daemon flags cannot reinterpret a historical
opaque slot, and changing policy kind cannot reinterpret signed state.

## Immutable image and execution boundary

Every persisted slot remains an owner-private, digest-named, mode-0400 regular file. It never gains
an executable permission bit. At service admission the adapter:

1. resolves the exact revision named by recovered device-signed state and the current pointer;
2. opens the slot no-follow, requires one link, exact owner/mode/size, and freezes its descriptor
   metadata;
3. copies it into an anonymous Linux memfd while recomputing SHA-256, then compares the exact byte
   count, digest, and before/after slot descriptor snapshot;
4. changes only the anonymous image to mode 0700;
5. adds and verifies F_SEAL_WRITE, F_SEAL_GROW, F_SEAL_SHRINK, and F_SEAL_SEAL;
6. opens the helper no-follow and requires a root- or daemon-owned executable regular file with no
   group/other write or special mode bits;
7. uses posix_spawn to enter the IoTox internal helper, avoiding post-fork C++ work in the
   multithreaded Agent;
8. requires the helper to validate the pipe/image descriptors, set close-on-exec on image and status
   descriptors, arm PR_SET_PDEATHSIG(SIGKILL) and PR_SET_NO_NEW_PRIVS, create a new session and
   process group, change to /, set umask 077, require Linux close_range, and finally fexecve the
   sealed descriptor.

Standard input is /dev/null. Standard output and error remain attached to the IoTox service
manager/logging boundary. The payload receives no caller-selected arguments and only this fixed
environment:

    IOTOX_SERVICE_READY_FD=3
    IOTOX_UPDATE_SEQUENCE=CANONICAL_DECIMAL
    IOTOX_UPDATE_VERSION=SIGNED_MANIFEST_VERSION
    IOTOX_UPDATE_PAYLOAD_DIGEST=UPPERCASE_SHA256

No release payload pathname is executed. No archive path, remote argv, shell, loader option, working
directory, environment addition, or health command enters through Tox.

## Health contract

After its own initialization and meaningful internal checks, the service writes exactly one
16-byte record to descriptor 3 and may close it:

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | ASCII IOTOXSR1 |
| 8 | 8 | exact release sequence, big-endian |

The adapter is ready only after accepting that exact record from the still-live process. Partial,
oversized, malformed, wrong-sequence, early-EOF, timeout, exec failure, or process-exit outcomes are
not healthy. update-confirm additionally re-polls the child and requires that the adapter still
names the exact signed candidate before checking the existing one-use token. The service readiness
claim cannot replace that token.

If an awaiting-health candidate fails, the Agent immediately invokes the existing signed rollback,
switches current back to the confirmed slot, terminates the failed service process group, and
launches the confirmed service through the complete verification/sealing path. The ordinary bounded
health deadline does the same. A second Agent restart still rolls back through the durable state
machine before service launch.

Confirmation promotes the live adapter instance from candidate to confirmed without executing a
second copy. A later crash of an already confirmed service is visible but does not silently lower the
confirmed release sequence. Restart policy for a confirmed crash belongs to the enclosing service
manager and must remain bounded; IoTox does not introduce an internal crash loop.

update-status reports the policy kind, adapter phase, PID, selected sequence, candidate/confirmed
classification, readiness, and sealed-image fact without service output or payload content.

## Service-manager and recovery contract

The reference deployment is a foreground Type=simple-style Linux service. The payload must not
daemonize or deliberately escape its process group. The enclosing manager must place IoTox and its
service descendants in one dedicated cgroup and use whole-cgroup shutdown semantics, such as systemd
KillMode=control-group. The internal process group closes ordinary descendants; the cgroup is the
required defense against a deliberately re-sessioned descendant after abrupt Agent death.

The owner must retain recovery media outside the writable update root containing:

- a known-good IoTox binary and its pinned runtime libraries;
- the latest reviewed update and sync policy;
- the device identity/authority recovery procedure and release-signer public records;
- a way to inspect or move current only through the documented signed-state recovery procedure;
- enough storage to preserve the confirmed slot and quarantine evidence.

For a boot-critical product, this service adapter is not the boot partition. A separately named A/B
boot adapter, bootloader success counter, read-only recovery partition, secure-boot chain, and
hardware monotonic witness remain required.

## Current qualification and nonclaims

Owned tests execute a real dynamically linked ELF fixture through the sealed memfd/helper path,
prove delayed readiness blocks confirmation, promote the exact live candidate, stop/reap it, then
stage an executable successor that exits before readiness and prove immediate signed rollback plus
relaunch of the prior confirmed service. Unit tests also reject opaque-kind confusion, digest drift,
persistent execute bits, and policy/state reinterpretation.

The accepted Sandwurm `update-service` cells run the same source-linked binary inside two
simultaneous guests over direct UDP and forced TCP. After authority-gated remote staging, the
subscriber kills the service before readiness, kills the Agent after readiness and proves the
parent-death service exit, withholds confirmation through health expiry, and finally confirms and
recovers the ready service across a clean Agent restart. Both compact proofs independently verify six
Agent restarts, three signed rollbacks, a sealed image, and all service observations; see
`evidence/2026-08-27-sandwurm-linux-service-update.md`.

This is construction evidence on Linux. It does not prove arbitrary vendor payload correctness, an
abrupt whole-VMM or physical power loss, a production service-manager/cgroup boundary, flash wear,
secure boot, hardware rollback resistance, recovery media, or a representative physical target.
Those gates remain explicit in the roadmap.
