# Resident services

Status: native generator and status evidence present. IoTox renders reviewed
service artifacts, records content-free shape receipts, and can write a
separate observed-state receipt after the operator has checked the service
manager, logs, health command, and upgrade check. It still does not silently
install units or claim unrelated sync/route/Ratox proof.

The resident surface is:

```sh
iotox service plan|render|receipt|status-plan|status-receipt \
  --target agent|person|all \
  --manager systemd-user|nixos-user|nixos-system|monsternix
```

Use it when a machine should keep IoTox running continuously:

- `agent` is the long-lived Agent path. It owns the ordinary `iotox run
  --config ROOT/agent.conf` process where sync, Ratox host/controller, route
  health, and control sockets live.
- `person` is the person messenger worker. It runs `iotox person
  background-run` over the local contact, seen, transcript, receipt, outbox,
  and dead-letter stores.
- `all` renders both.

Example for an owner user service:

```sh
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox init write-config --root ~/.local/state/iotox --mode self --enable-sync
iotox config-lint ~/.local/state/iotox/agent.conf

iotox service plan \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox

iotox service render \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --raw

iotox service receipt \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --accept-operator-responsibility \
  --out ~/.local/state/iotox/resident-service.receipt

iotox service status-plan \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox

iotox service status-receipt \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --service-manager-state active \
  --enabled-state enabled \
  --log-state reviewed \
  --health-state passed \
  --upgrade-state passed \
  --accept-operator-responsibility \
  --out ~/.local/state/iotox/service-reality.receipt
```

The plan prints the exact render, raw service-file, and receipt commands plus
the service-manager enable/log/disable commands for the selected manager. For
systemd-user that is ordinary `systemctl --user enable --now ...` and
`journalctl --user -u ... -f`. For NixOS it is a module fragment to review,
import, rebuild, and switch. For MonsterNix it is an adapter draft: IoTox names
the command and health shape; MonsterNix remains responsible for source,
package, proof, activation, logs, rollback, and host policy.

`service receipt` and `service status-receipt` are intentionally different:

- `service receipt` says the rendered service shape was reviewed. It records
  `not-service-manager-state-proof=1`.
- `service status-plan` prints the active/enabled/log/health/upgrade checks to
  run for the selected manager.
- `service status-receipt` records the result only when the operator supplies
  `service-manager-state=active`, `enabled-state=enabled|static|managed`,
  `log-state=reviewed`, `health-state=passed`, and `upgrade-state=passed`
  with `--accept-operator-responsibility`.

Upgrade rule: replace the binary through the package manager or MonsterNix
path first, run the printed `run-check`/health command, review recent logs, and
only then write a new status receipt. The status receipt is accepted stable
evidence for `terminal.service-supervision`; it is not proof of cgroup
delegation, route loss, sync folder health, or person read semantics.

Useful post-activation checks:

```sh
iotox overview
iotox readiness
iotox --runtime ~/.local/state/iotox/runtime status
iotox person messenger-status \
  --contacts ~/.local/state/iotox/person.contacts \
  --seen ~/.local/state/iotox/person.seen \
  --transcript ~/.local/state/iotox/person.transcript \
  --receipts ~/.local/state/iotox/person.receipts \
  --outbox ~/.local/state/iotox/person.outbox
iotox terminal activation-check --root ~/.local/state/iotox --peer alias:desktop
```

Stable dossier path:

```sh
iotox evidence collect terminal \
  --root ~/.local/state/iotox \
  --peer alias:desktop \
  --out /proof/stable \
  --service-reality ~/.local/state/iotox/service-reality.receipt \
  --long-soak /proof/terminal-24h.receipt \
  --evidence daily-control=local.gate \
  --evidence profile-freshness=profile.check \
  --evidence reconnect-continuity=cli.reconnect \
  --evidence cgroup-delegation=nixos.cgroup \
  --evidence route-loss=tox.loss \
  --evidence tor-route-loss=tor.operator \
  --evidence i2p-route-loss=i2p.fronts \
  --evidence sudo-policy=host.sudo \
  --evidence security-review=owner.review \
  --evidence activation-decision=owner.decree
```

Nonclaims:

- no automatic installation without operator review;
- no hidden service-manager query or remote attestation;
- no proof that sync folders are healthy or precious-data signed off;
- no proof that Ratox cgroups, sudo policy, or route loss have graduated; and
- no proof that a human read a message.
