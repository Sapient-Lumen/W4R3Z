# NixOS deployment example

Status: example only. IoTox does not mutate `configuration.nix`.

This page shows the shape of a NixOS user service around the native IoTox
binary. The operator still owns config review, RecallRoot custody, peer grants,
terminal profile policy, sudoers/PAM policy, recovery-custody evidence, and service
activation.

Prefer the top-level native renderer when drafting the module fragment. It can
render the Agent/sync/Ratox service and the person messenger worker together:

```sh
iotox service plan --target all --root /var/lib/iotox \
  --manager nixos-system \
  --unit-prefix iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox

iotox service render --target all --root /var/lib/iotox \
  --manager nixos-system \
  --unit-prefix iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox \
  --raw

iotox service receipt --target all --root /var/lib/iotox \
  --manager nixos-system \
  --unit-prefix iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox \
  --accept-operator-responsibility \
  --out /var/lib/iotox/resident-service.receipt

iotox service status-plan --target all --root /var/lib/iotox \
  --manager nixos-system \
  --unit-prefix iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox

iotox service status-receipt --target all --root /var/lib/iotox \
  --manager nixos-system \
  --unit-prefix iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox \
  --service-manager-state active \
  --enabled-state enabled \
  --log-state reviewed \
  --health-state passed \
  --upgrade-state passed \
  --accept-operator-responsibility \
  --out /var/lib/iotox/service-reality.receipt
```

For a legacy terminal-only service-shape receipt, use the terminal-specific
renderer:

```sh
iotox terminal service plan --root /var/lib/iotox \
  --manager nixos-system \
  --unit iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox

iotox terminal service render --root /var/lib/iotox \
  --manager nixos-system \
  --unit iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox \
  --raw

iotox terminal service receipt --root /var/lib/iotox \
  --manager nixos-system \
  --unit iotox \
  --user iotox \
  --binary /run/current-system/sw/bin/iotox \
  --accept-operator-responsibility \
  --out /var/lib/iotox/terminal-service.receipt
```

Prefer the top-level `service status-receipt` for the
`terminal.service-supervision` stable dossier gate after the NixOS switch has
made the unit active and enabled. The legacy receipt label
`service-supervision=terminal.service.nixos-system` remains useful for
terminal activation/graduation operator evidence after you have reviewed the
rendered unit shape and separately verified the service-manager state.

## Native IoTox config first

Create the Agent argument record with the binary, not by hand:

```sh
iotox init plan --root /var/lib/iotox --mode self --enable-sync
sudo install -d -m 700 -o "$USER" -g "$(id -gn)" /var/lib/iotox
iotox init write-config --root /var/lib/iotox --mode self --enable-sync
iotox config-lint /var/lib/iotox/agent.conf
```

For system services, paths and ownership should be changed deliberately for the
chosen service user. Do not put RecallRoot phrases, private keys, or shell
expansion into the config file. Self mode selects Ratox host/controller roles,
but terminal preflight still requires an installed profile, a binding, and
`interactive.terminal` authority before `run-check` can declare terminal
readiness.

## Sketch module fragment

This is intentionally a sketch. The native renderer emits a smaller fragment;
replace package and user paths with the exact derivation and deployment model
you use:

```nix
{ config, pkgs, lib, ... }:

let
  iotox = pkgs.callPackage ./path/to/iotox-package.nix {};
in
{
  users.users.iotox = {
    isSystemUser = true;
    group = "iotox";
    home = "/var/lib/iotox";
    createHome = true;
  };
  users.groups.iotox = {};

  systemd.services.iotox = {
    description = "IoTox Agent";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    wants = [ "network-online.target" ];
    serviceConfig = {
      User = "iotox";
      Group = "iotox";
      Type = "simple";
      ExecStartPre = [
        "${iotox}/bin/iotox config-lint /var/lib/iotox/agent.conf"
        "${iotox}/bin/iotox run-check --config /var/lib/iotox/agent.conf"
      ];
      ExecStart = "${iotox}/bin/iotox run --config /var/lib/iotox/agent.conf";
      Restart = "on-failure";
      RestartSec = "5s";
      NoNewPrivileges = true;
      PrivateTmp = true;
      ProtectSystem = "strict";
      ReadWritePaths = [ "/var/lib/iotox" ];
    };
  };
}
```

For Ratox cgroup delegation, use a dedicated reviewed unit shape with systemd
delegation and then validate:

```sh
iotox terminal doctor
```

If sudo is needed inside Ratox, create and bind an explicit admin profile:

```sh
iotox terminal profile plan sudo owner-admin iotox --store /var/lib/iotox/ratox
```

IoTox does not grant root. The host sudoers/PAM policy remains the authority.

## Post-activation checks

```sh
iotox overview
iotox readiness
iotox help pairing
iotox help sync
iotox help terminal
```

Keep `iotox readiness storage` blocked for precious data until independent
backup custody and restore rehearsal are proven for the deployment.
