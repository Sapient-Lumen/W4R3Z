# systemd deployment example

Status: example only. IoTox does not install this unit automatically.

This is a small owner-local service shape for a machine where the operator has
already reviewed the state root, runtime root, route, sync, and terminal policy.
The service uses the canonical config file path and runs the same nonmutating
check before starting the long-lived Agent.

Prefer the top-level native generator over copying this page by hand. It can
render the Agent/sync/Ratox service and the person messenger worker together:

```sh
iotox service plan --target all --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox

iotox service render --target all --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --raw

iotox service receipt --target all --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --accept-operator-responsibility \
  --out ~/.local/state/iotox/resident-service.receipt

iotox service status-plan --target all --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox

iotox service status-receipt --target all --root ~/.local/state/iotox \
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

For a legacy terminal-only service-shape receipt, use the terminal-specific
generator:

```sh
iotox terminal service plan --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit iotox-self \
  --binary /usr/bin/iotox

iotox terminal service render --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit iotox-self \
  --binary /usr/bin/iotox \
  --raw > ~/.config/systemd/user/iotox-self.service

iotox terminal service receipt --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit iotox-self \
  --binary /usr/bin/iotox \
  --accept-operator-responsibility \
  --out ~/.local/state/iotox/terminal-service.receipt
```

The terminal-specific receipt is content-free and useful as an operator record,
but it is not proof that systemd is active, cgroups are delegated, routes
survive impairment, or sudo policy is correct. Prefer the top-level
`service status-receipt` for the `terminal.service-supervision` stable dossier
gate. The old activation label still works for daily activation/graduation
operator evidence:

```sh
iotox terminal activation-check --root ~/.local/state/iotox \
  --peer alias:desktop \
  --evidence service-supervision=terminal.service.systemd-user \
  --evidence daily-control=local.gate \
  --evidence profile-freshness=profile.check \
  --evidence reconnect-continuity=cli.reconnect \
  --evidence cgroup-delegation=nixos.cgroup \
  --evidence route-loss=tox.loss
```

## Prepare reviewed config

```sh
install -d -m 700 ~/.local/state/iotox
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox init write-config --root ~/.local/state/iotox --mode self --enable-sync
iotox config-lint ~/.local/state/iotox/agent.conf
```

`init write-config` does not create RecallRoot authority, grant peers, install
terminal profiles, enable sudo, or certify backup readiness. In self mode it
does select Ratox host/controller roles by default; install and bind a reviewed
profile, then run `run-check`, as separate reviewed steps.

## User service sketch

The native render command emits a conservative unit. This is the rough shape it
should resemble after replacing absolute paths:

```ini
[Unit]
Description=IoTox self-machine agent
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStartPre=/usr/bin/iotox run-check --config %h/.local/state/iotox/agent.conf
ExecStart=/usr/bin/iotox run --config %h/.local/state/iotox/agent.conf
Restart=on-failure
RestartSec=2s
UMask=0077
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=default.target
```

Enable only after the preflight commands pass manually:

```sh
systemctl --user daemon-reload
systemctl --user enable --now iotox.service
iotox overview
iotox readiness
```

If Ratox delegated cgroups are required, the final service manager shape is
host-specific. Validate with `iotox terminal doctor` and the cgroup/PSI gates
documented in `docs/ratox-ssh-status.md`.

## Support bundle review

When asking for help, plan and inspect the support artifact before sharing:

```sh
iotox support-bundle plan ./iotox.support
iotox support-bundle create ./iotox.support
iotox support-bundle inspect ./iotox.support
```

The bundle is content-free, not information-free, and is not remote attestation
or backup proof.
