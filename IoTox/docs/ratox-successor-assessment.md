# Ratox successor assessment

This document records the rev0015 product decision and its historical evidence boundary. The
current implemented terminal and SSH-shaped nonclaims are maintained in `ratox-ssh-status.md`.

## Decision

IoTox should continue as a modern ratox successor built around current c-toxcore, not as a patch set
on the historical ratox implementation and not as a rewrite of Tox itself.

The product principle is:

> Keep ratox's ordinary Unix joy. Replace implicit state with exact typed semantics underneath.

## What must be preserved

ratox's strongest ideas are still correct:

- one small daemon can make encrypted peer networking feel ordinary;
- files, FIFOs, and directories compose with shell, C++, supervisors, and existing Unix tools;
- local state and identity do not require a vendor account;
- an owner can inspect and automate the client without embedding a networking SDK;
- initiation, text, files, and lifecycle operations can “just werx.”

IoTox should remain friendly to this style:

```sh
printf '%s\t%s\n' "$TOX_ADDRESS" 'hello from my device' > "$RUNTIME/request"
printf '%s\n' 'hello' > "$RUNTIME/peers/$KEY/message"
printf '%s\n' accept > "$RUNTIME/requests/$KEY/accept"
```

## What must not be inherited blindly

A production device agent cannot make a FIFO carry meanings it does not possess. IoTox therefore
must not inherit:

- one monolithic global-state translation unit;
- friendship as authorization;
- numeric friend numbers as durable identity;
- first-whitespace or C-string-shaped binary parsing;
- FIFO buffering as an offline queue;
- write success as remote or execution success;
- conflated file-transfer state;
- in-place identity truncation;
- direct dependence on unstable toxcore structure layout;
- silent network-route fallback.

## What rev0015 adds to the succession

rev0015 closes the most visible remaining ratox friendship gap: outgoing request by one ordinary root
write.

The record is exact rather than shell-shaped:

```text
76 address hex bytes
1 literal TAB
1..921 message bytes
1 LF framing byte
```

The full 38-byte address reaches `tox_friend_add`; the public-key prefix becomes the stable local peer
selector. The message preserves every non-LF byte. No default message or whitespace search invents
meaning.

The same Agent method serves the root FIFO and structured local protocol. Only the toxcore owner
thread calls the provider. The ordinary adapter does not create a second state machine, permission
model, retry loop, or durable queue.

The generalized FIFO service now supports both public-key directory lanes and required root lanes
under one hardening contract:

- no symlink following;
- daemon owner and private mode;
- opened inode matches inspected inode;
- actual `PIPE_BUF` supports the maximum atomic record;
- bounded buffering and abandoned partial-record expiry;
- safe rescan and replacement;
- readiness drops when a promised root FIFO disappears.

Malformed records create explicit `public-key=unknown` evidence when no key can be trusted. IoTox no
longer needs a fabricated all-zero identity to fit a journal shape.

## Deliberate differences from ratox

ratox's global input splits on first whitespace and historically supplies a default request string.
IoTox requires the caller to own every byte. TAB is one exact boundary, and an empty message is
invalid because the provider contract says it is invalid.

ratox makes compact direct calls from its event loop. IoTox uses:

```text
local adapter -> Agent -> bounded command -> exclusive toxcore owner
```

This is heavier inside and simpler to reason about. It permits the same operation to be called from a
FIFO, the one-binary CLI, tests, and future local clients without multiplying provider rules.

IoTox also keeps application authority above transport friendship. Adding a Tox friend never grants
an owner role, device capability, firmware permission, or physical effect.

## Current evidence boundary

The root FIFO, typed operation, owner-thread call, mock provider result, lifecycle journal, peer
projection, restart, and public-key removal are exercised in C++ and in a separate actual `iotox run`
process.

At rev0015, the later official-repository work had only added the pinned source-linked binary and a
two-genuine-peer native smoke. At that historical boundary it did not prove:

- repeatable public-network, NAT, relay, or cross-client behavior;
- independently reproducible packaging;
- Tor/I2P containment;
- target-hardware resource or power behavior.

Later revisions qualified bounded Tor/I2P containment and much broader Sandwurm behavior; ADR 0277
retired independent-builder and target-hardware evidence from repository completion. The current
claim and nonclaims live in `ratox-ssh-status.md`; this historical list is not an open roadmap.

## Current direction

The diagnostic-era next steps above have been completed. Ratox v1 now has frozen packet `0xA2`
framing, exact terminal authority, owner-selected profile v5, a real PTY adapter, Agent dispatch, a
private local controller, `terminal`/`terminal-resume`, route reconnect and explicit resume,
seccomp/Landlock/MDWE/cgroup/PSI construction hardening, and retained two-guest latency, load,
impairment, and total-loss evidence. It remains explicitly default off.

The founding-machine Ratox construction is complete. Optional operational R8—named deployment-
kernel/service-manager qualification, positive controller/PSI outcome evidence, independent review,
long soaks, and a deliberate production-support activation decision—remains outside repository
completion. SSH-like local ergonomics—profile administration,
session listing/close, and batch stdin/stdout—are planned but absent. Arbitrary remote commands,
forwarding, agent forwarding, SFTP/SCP compatibility, and daemon-restart PTY persistence are not
implemented. See `ratox-ssh-status.md` for the exact boundary.

The local surface should keep getting easier to use. The inner semantics should keep getting harder
to lie about.
