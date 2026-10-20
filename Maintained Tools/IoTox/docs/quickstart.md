# IoTox quickstart

Status: short human entrance. Updated 2026-10-01.

This is the first-hour path. It deliberately uses reviewed porches and dry-run
plans before mutation. It does not replace the roadmap, threat model, or
deployment docs.

## First sentence

IoTox lets you pair owned machines, join them into a self-machine control
swarm, sync ordinary directories, and open an owner-approved shell over Tox;
friendship, self authority, sync, sudo, support, and backup remain separate
boundaries.

## 0. Ask the binary what is safe

```sh
iotox help
iotox help quickstart
iotox help shipping
iotox help support
iotox doctor binary
iotox overview
iotox readiness
```

If the Agent is offline, `overview` and `readiness` still give conservative
guidance. They do not start an Agent for you. `doctor binary` is content-free;
it tells you the compiled IoTox version/revision, the executable path, the
build-time source commit when embedded, and whether the current directory's
`REVISION` file matches the binary's compiled revision.

## 1. Create a reviewed local Agent config

Choose one private state root. For a user service:

```sh
install -d -m 700 ~/.local/state/iotox
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox init write-config --root ~/.local/state/iotox --mode self --enable-sync
iotox config-lint ~/.local/state/iotox/agent.conf
```

`--mode self` makes the Ratox host and local terminal controller selected by
default, but terminal readiness still needs an installed profile, a binding, and
`interactive.terminal` authority. After those are reviewed, preflight and run
manually while learning:

```sh
iotox run-check --config ~/.local/state/iotox/agent.conf
iotox run --config ~/.local/state/iotox/agent.conf
```

For the native resident-service porch, see `docs/resident-services.md`; for
host-specific examples, see `docs/deploy-systemd.md` and
`docs/deploy-nixos.md`. Service rendering does not create owner authority,
grant peers, install terminal profiles, enable sudo, prove routes, or certify
backups.

## 2. Pair two machines without granting authority

On the inviting machine:

```sh
iotox pair-card create ./workstation.iotox-invitation \
  --expires 86400 --alias workstation \
  --capabilities sync.subscribe,sync.publish
```

Move the card by any channel. Move the expected inviter stable principal by a
separate trusted channel.

On the receiving machine:

```sh
iotox pair-card inspect ./workstation.iotox-invitation EXPECTED_INVITER_PUBLIC_KEY
iotox pair-card accept ./workstation.iotox-invitation EXPECTED_INVITER_PUBLIC_KEY \
  --alias workstation
```

Boundary: pair cards introduce transport and optional alias. They still print
`authority-granted=0`.

## 3. Join the self swarm before granting shell authority

Pairing is not authority. For machines you own, create or update the
owner-signed self roster, then grant one reviewed member at a time:

```sh
cat RECALLROOT.txt | \
  iotox self-swarm create-recall-stdin ~/.local/state/iotox/self.swarm \
    desktop DESKTOP_PRINCIPAL_HEX DESKTOP_TOX_KEY_HEX \
    operator interactive.terminal

cat RECALLROOT.txt | \
  iotox self-swarm join-recall-stdin ~/.local/state/iotox/self.swarm \
    workstation WORKSTATION_PRINCIPAL_HEX WORKSTATION_TOX_KEY_HEX \
    operator interactive.terminal,sync.subscribe

iotox self-swarm verify ~/.local/state/iotox/self.swarm \
  --min-generation 2 \
  --expect-member workstation WORKSTATION_PRINCIPAL_HEX \
  --expect-route workstation WORKSTATION_TOX_KEY_HEX

iotox self-swarm grant-plan ~/.local/state/iotox/self.swarm --from desktop

cat RECALLROOT.txt | \
  iotox self-swarm grant-recall-stdin ~/.local/state/iotox/self.swarm workstation \
    --min-generation 2 \
    --expect-member workstation WORKSTATION_PRINCIPAL_HEX \
    --expect-route workstation WORKSTATION_TOX_KEY_HEX
```

Boundary: the roster is reviewable membership, not a second authority ledger.
It helps produce exact authority operations; it does not install profiles,
enable sudo, or make a Tox friend into a shell.

## 4. Practice sync before precious data

Create a disposable private directory:

```sh
mkdir -p ~/iotox-practice
chmod 700 ~/iotox-practice
printf 'hello from %s\n' "$(hostname)" > ~/iotox-practice/hello.txt
iotox sync-doctor ~/iotox-practice read-write 30
```

Plan the pair before mutating:

```sh
iotox sync plan-pair practice ~/iotox-practice alias:workstation \
  /home/USER/iotox-practice read-write 30
```

If the plan is acceptable, each side creates its own local namespace and then
each side shares with the other:

```sh
iotox sync start practice ~/iotox-practice read-write 30
cat RECALLROOT.txt | \
  iotox sync share practice alias:workstation read-write
iotox sync-status
iotox sync-health practice cached
```

`RECALLROOT.txt` is a placeholder for a private local ceremony input. The
phrase is read from stdin; do not put it in argv or environment variables, and
protect or destroy any temporary file used to feed stdin.

Boundary: IoTox sync can be a useful working copy. It is not the backup. Do
not start with a beloved directory.

## 5. Plan an owner-approved terminal profile

Self mode already selects the Ratox host/controller. This section decides what
a proved self peer may actually reach.

Check this host first:

```sh
iotox terminal doctor
```

Plan a normal shell profile:

```sh
iotox terminal profile plan shell owner-shell "$USER"
```

If you need sudo, plan it as a separate explicit profile:

```sh
iotox terminal profile plan sudo owner-admin "$USER"
```

Boundary: IoTox does not grant root. The host's sudoers/PAM policy decides
inside the approved profile. The peer does not select argv, shell, sudo bit, or
port forwarding.

## 6. Ask for help without leaking content

```sh
iotox support-bundle plan ./iotox.support
iotox support-bundle create ./iotox.support
iotox support-bundle inspect ./iotox.support
```

Boundary: support bundles are content-free, not information-free, and are not
remote attestation or backup proof.

## 7. Package a clean public repo snapshot

When you want another person, GitHub upload, or ChatGPT session to review the
exact repository, use the seed datacube profile from a clean committed tree:

```sh
tools/iotox-repo.sh release-plan founder-preview
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --seed
```

Use `tools/iotox-repo.sh datacube --upload` only when the recipient needs full
local Git history. Use `tools/iotox-repo.sh datacube --conversation` only when
the recipient needs the richer internal conversation/recovery cube with nested
founding-cube provenance.
Datacubes are exact-state handoff objects; they are not release authority or a
substitute for `iotox ship-check`.

## Next reading

- `docs/README.md` for the documentation map;
- `docs/edge-of-hope.md` for the ideal;
- `docs/pragmatic-guardrails.md` for the nonclaims;
- `docs/replace-resilio-sync.md` for sync migration thinking;
- `docs/everyday-sync-plan.md` for detailed sync commands;
- `docs/resident-services.md` for systemd/NixOS/MonsterNix resident services;
- `docs/self-mode.md` for self-machine Ratox defaults and signed roster work;
- `docs/ratox-ssh-status.md` for terminal/SSH-shaped control;
- `docs/storage-readiness-gates.md` for precious-data boundaries.
