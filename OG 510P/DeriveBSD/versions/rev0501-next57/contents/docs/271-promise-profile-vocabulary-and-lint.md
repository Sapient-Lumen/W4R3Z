# Promise profile vocabulary + lint rules (v0)

Promise profiles (`sandbox-profile`) are meant to deliver the *pledge/unveil superpower*: a **tiny, reviewable declaration** that engineers can apply everywhere.

This doc defines:
- the **curated promise vocabulary** (what the strings in `promises[]` mean)
- the **lint rules** we should enforce so profiles don’t devolve into “allow everything”

See:
- Promise profiles overview: `docs/232-service-promise-profiles.md` (RFC-0166)
- Schema + example: `spec/sandbox.profile.schema.json`, `spec/examples/sandbox.profile.json`
- Network egress broker + consent: `docs/281-network-egress-broker-and-consent.md` (egress classes via `spec/net.egress.policy.schema.json`)
- Inbound listen broker + firewall leases: `docs/286-inbound-listen-broker-and-firewall-leases.md` (listen classes via `spec/net.listen.policy.schema.json`)

## Design constraints

1) **Small vocabulary**
- We only add a new promise when multiple real programs need it.
- A promise must compile to concrete enforcement (jail view / capsicum rights / portal grants / MAC knobs).

2) **Fail-closed defaults**
- No ambient networking.
- No ambient filesystem.
- If something must be “late-bound”, it goes through a broker (portal/powerbox).

3) **Authority edits are code-review events**
- Changing a profile is changing authority.
- Loosening a profile SHOULD require a policy decision record.

## Curated promises (initial set)

This is an intentionally **minimal** pledge-shaped vocabulary. It is *not* a syscall filter DSL.

### Base

- `stdio`
  - May use stdin/stdout/stderr.
  - No filesystem access unless also granted by `fs.rules` and jail mounts.

- `rpath`
  - Intent: read files.
  - Compiles to: allowlisted read-only mounts + capsicum fd rights on preopened descriptors.

- `wpath`
  - Intent: write existing files.
  - Compiles to: allowlisted writable mounts + capsicum fd rights on preopened descriptors.

- `cpath`
  - Intent: create files.
  - Compiles to: allowlisted writable mounts + directory create rights.

### Process + execution

- `proc`
  - Intent: limited process inspection (e.g. self + children).
  - Compiles to: jail namespace constraints + restricted procfs exposure (if any).

- `exec`
  - Intent: spawn child processes.
  - Compiles to: allowlist execution roots in the jail view; prefer “wrapper binaries” so exec intent is reviewable.

### Networking

- `dns`
  - Intent: name resolution.
  - Compiles to: prefer Casper `system.dns` (or an explicit DNS portal), rather than ambient `/etc/resolv.conf` + raw sockets.

- `inet`
  - Intent: outbound network.
  - Compiles to: **network egress broker** grants (`net.egress_classes[]`, defined by `spec/net.egress.policy.schema.json`) + PF egress policy (preferred).
  - Note: Capsicum does not automatically eliminate socket authority; treat `inet` as a high-risk promise.

- `inet-listen`
  - Intent: bind/listen on network sockets (inbound exposure).
  - Compiles to: **listen broker** grants (`net.listen_classes[]`, defined by `spec/net.listen.policy.schema.json`) + PF anchors for inbound policy.
  - Default: prefer socket activation so services don’t own long-lived listener authority.

### Devices

Device nodes are ambient authority. Promise profiles should never get “whatever /dev contains”.

- `device:audio`
  - Intent: access microphone/speaker.
  - Default direction: broker via portals where possible; if direct nodes exist, expose only the minimal device nodes via devfs rules (jails) and bind to a device lease (`spec/device.attach.grant.schema.json`).

- `device:camera`
  - Intent: access a camera.
  - Default direction: portal/broker strongly preferred; direct device nodes should be opt-in and visible in diffs.

- `device:block:ro`
  - Intent: read from removable/block storage.
  - Compiles to: **read-only** device lease + minimal `/dev` exposure; prefer attaching partitions rather than whole disks.

- `device:block:rw`
  - Intent: write to block storage.
  - Lint: should require policy decision record or breakglass, and should default to TTL + explicit target device ids.

See: `docs/278-device-grants-and-devfs-rulesets.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`.

### Interactive exceptions

- `portal`
  - Intent: the service/app may request portal surfaces listed in `portals[]`.
  - Compiles to: explicit portal allowlists + audited portal session receipts.

## Lint rules (what we should enforce early)

The goal is to keep profiles *boringly safe* and prevent “security theater” profiles.

### 1) Networking must be explicit and brokered

- If `promises[]` contains `inet`, then either:
  - `net.egress_classes[]` MUST be non-empty (preferred), or
  - the profile MUST explicitly set `meta.allow_ambient_network=true` (discouraged; should trigger a policy record).

- If `net.egress_classes[]` is present, `promises[]` MUST include `inet`.

- If `promises[]` contains `inet-listen`, then either:
  - `net.listen_classes[]` MUST be non-empty (preferred), or
  - the profile MUST explicitly set `meta.allow_ambient_listen=true` (discouraged; should trigger a policy record).

- If `net.listen_classes[]` is present, `promises[]` MUST include `inet-listen`.

### 2) Filesystem rules must not be “the whole machine”

- `fs.rules[].path` MUST NOT be `/`.
- Broad prefixes like `/usr` or `/home` SHOULD require a policy record (and should be rare).
- If `fs.lock=true`, then the runtime MUST prevent further rule extension (monotonic tightening).

### 3) Portals and filesystem access shouldn’t conflict

- If `portals[]` includes high-risk surfaces (documents, clipboard, screencast), warn if:
  - `fs.rules` contains broad `rw/c` access.

Rationale: portal surfaces already represent “late-bound” authority; combining them with broad filesystem access makes review meaningless.

### 4) Profiles should be small enough to reason about

- Cap the number of `promises[]` entries (e.g. 12) and `fs.rules` entries (e.g. 32) unless a policy record is attached.

### 5) Profile names are stable API

- `name` must be stable and versioned (`profile:<role>@<n>`).
- A new major version means the meaning changed (not just the permissions).

## Example profile shapes

- Fetcher (tight): see `spec/examples/sandbox.profile.json`.
- Builder (typical): `stdio`, `rpath`, `wpath`, `cpath` + no `inet`.
- Portalized desktop app (interactive): minimal FS + `portal` + explicit portals (documents/clipboard/etc.), but no broad `rw`.

Last updated: 2026-02-25
