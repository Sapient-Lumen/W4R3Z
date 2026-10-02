# IoTox documentation map

Status: human-facing docs index. Updated 2026-10-01.

```text
IoTox is a device nerve:
  memory proves ownership
  Tox reaches the peer
  the ledger grants the act
  Unix makes it operable
  evidence keeps it honest
```

If you are new, do not start with the ADRs. Start with the shape of the
product, then choose the operator surface you care about.

## First doors

- [`product-page.md`](product-page.md): the public explanation with the
  project voice.
- [`quickstart.md`](quickstart.md): the first safe hour on a machine you own.
- [`ship-readiness.md`](ship-readiness.md): what founder-preview and stable
  actually mean.
- [`roadmap.md`](roadmap.md): the ordered plan and current frontier.
- [`pragmatic-guardrails.md`](pragmatic-guardrails.md): the nonclaims that keep
  the project sane.
- [`edge-of-hope.md`](edge-of-hope.md): the north star when the tool grows up.

## Operator surfaces

| If you want to... | Read this |
| --- | --- |
| Replace an everyday sync tool for noncritical working folders | [`replace-resilio-sync.md`](replace-resilio-sync.md), [`everyday-sync-plan.md`](everyday-sync-plan.md), [`sync-health.md`](sync-health.md) |
| Decide whether a folder is safe enough for important data | [`sync-trust-graduation.md`](sync-trust-graduation.md), [`storage-readiness-gates.md`](storage-readiness-gates.md), [`sync-recovery-rehearsal.md`](sync-recovery-rehearsal.md) |
| SSH into your own machines through IoTox | [`ratox-ssh-status.md`](ratox-ssh-status.md), [`self-mode.md`](self-mode.md), [`terminal-client-v1.md`](terminal-client-v1.md) |
| Run IoTox continuously | [`resident-services.md`](resident-services.md), [`deploy-systemd.md`](deploy-systemd.md), [`deploy-nixos.md`](deploy-nixos.md) |
| Understand one person key across many devices | [`person-multidevice.md`](person-multidevice.md) |
| Package the repo for another reviewer or ChatGPT session | [`conversation-datacubes.md`](conversation-datacubes.md), [`revision-packaging.md`](revision-packaging.md), [`publication-boundary.md`](publication-boundary.md) |
| Change architecture without blurring boundaries | [`architectural-change-intake.md`](architectural-change-intake.md) |

## Current truth, in plain words

- Sync is useful as a working-copy synchronizer and has substantial local
  evidence, recovery rehearsal, conflict preservation, and precious-data
  signoff tooling. It is not the backup and is not trying to become the
  disk-loss, host-compromise, filesystem-wide-corruption, or storage-media
  certification layer.
- Ratox is the SSH-shaped control surface for machines you own. It is
  profile-bound, sudo-denied by default, and meant to become daily-driver
  boring without becoming arbitrary remote exec.
- Self mode is the private machine roster above Tox's missing multidevice
  story. A friendship or savedata key does not become shell authority by
  itself.
- Person multidevice messaging has the main product primitives: delivery cards,
  device fanout, delegated send, receipts, read-status, groups, background
  worker planning, and a Toxic-compatible bridge. Global ordering, universal
  client compatibility, and perfect “human read this” semantics are not claimed.
- Tor/I2P support is explicit route construction with bounded evidence, not a
  marketing claim about anonymity or reliability.
- Public handoff should usually be the seed
  `IoTox-seed-repository-datacube-...zip`: exact source, one-commit cloneable
  bundle, no local history. Full-history
  `IoTox-upload-repository-datacube-...zip` remains a private provenance
  object; rich conversation cubes remain available when a reviewer needs nested
  provenance.

## Native porch commands to remember

```sh
iotox help
iotox help quickstart
iotox help routes
iotox help evidence
iotox help shipping
iotox help support
iotox help all
iotox doctor binary
iotox overview
iotox readiness
iotox explain TOPIC
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox sync plan-pair NAME LOCAL_PATH alias:PEER REMOTE_PATH read-write 30
iotox terminal doctor
iotox terminal profile plan shell owner-shell "$USER"
iotox service plan --target all --root ~/.local/state/iotox --manager systemd-user
iotox person quickstart
iotox person graduation-check
iotox ship-check all founder-preview
iotox support-bundle plan ./iotox.support
```

Repository handoff:

```sh
tools/iotox-repo.sh release-plan founder-preview
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --seed
```

## Reading style

IoTox docs use evidence-shaped language on purpose. “Passed” means a named
gate passed under its described scope. “Stable” means the binary accepted a
specific evidence manifest. “Founder-preview” means the founder can dogfood
with explicit nonclaims attached. When the docs sound cautious, that caution is
part of the product.
