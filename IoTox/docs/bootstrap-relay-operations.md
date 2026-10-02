# Owner-operated Tox bootstrap and relay service

IoTox includes a source-pinned c-toxcore bootstrap/TCP-relay package and an opt-in NixOS module.
The service is infrastructure an owner may contribute to the Tox network; it is not an IoTox
account plane, ownership service, recovery authority, or required dependency. Importing the module
opens no port and starts no process. Enabling it still requires an explicit reviewed package, and
the host firewall remains closed unless the operator opts in separately.

The daemon's node key controls only continuity of its public Tox node record. It grants no IoTox
device role or capability. A bootstrap or relay operator can observe network metadata and deny
service, but cannot reassign a device, modify its authority ledger, authorize a command, accept a
synchronization HEAD, or apply an update.

## Build and configure

Build the exact package without starting it:

```sh
nix build .#toxBootstrap
```

An external NixOS flake can import the module explicitly:

```nix
{
  inputs.iotox.url = "git+file:/absolute/path/to/IoTox";

  outputs = { nixpkgs, iotox, ... }: {
    nixosConfigurations.relay-host = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        iotox.nixosModules.toxBootstrap
        ({ pkgs, ... }: {
          services.iotox.toxBootstrap = {
            enable = true;
            package = iotox.packages.${pkgs.system}.toxBootstrap;
            addressFamily = "ipv4";
            openFirewall = true;

            # Review this record out of band. Omitting it creates an isolated
            # node; the module never downloads or invents a seed endpoint.
            bootstrapPeer = {
              address = "198.51.100.10";
              port = 33445;
              publicKey = "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF";
            };

            memoryMax = "256M";
            cpuQuota = "50%";
            tasksMax = 64;
          };
        })
      ];
    };
  };
}
```

Evaluate before activation, then use the ordinary NixOS deployment boundary:

```sh
nix flake check
sudo nixos-rebuild test --flake .#relay-host
sudo nixos-rebuild switch --flake .#relay-host
```

The pinned package deliberately exposes only TCP and UDP port 33445. It removes the upstream sample
daemon's extra TCP listeners on privileged/common ports 443 and 3389 and fixes its unconditional
stale-`errno` initialization message. `openFirewall = true` opens both protocols on the NixOS host;
it does not configure a router, NAT, provider security group, DNS, or upstream rate limit. Public
operation normally requires forwarding both TCP and UDP 33445 and verifying each from outside the
operator's network.

`addressFamily` selects the daemon's wildcard socket family. It is not an interface allowlist. Use
host/provider firewall policy when the service should bind only within a narrower trust boundary.

## Identity and state

systemd owns `/var/lib/iotox-tox-bootstrap` as a mode-0700 `StateDirectory` for a `DynamicUser`.
The apparent path may resolve beneath `/var/lib/private`; always address it through the stable public
path. On first successful start the daemon creates:

```text
key            64-byte private node key, mode 0600
PUBLIC_ID.txt  64 uppercase hexadecimal public key, mode 0600
```

The unit refuses symlinks, non-regular files, wrong lengths, permissive modes, or a malformed public
identifier before starting. Read the publishable identifier with:

```sh
sudo cat /var/lib/iotox-tox-bootstrap/PUBLIC_ID.txt
```

Distribute only `PUBLIC_ID.txt`'s value together with the operator-controlled public address and
port. Never publish `key`. An IoTox user can opt into the record independently:

```sh
iotox run \
  --bootstrap PUBLIC_ADDRESS:33445:PUBLIC_ID \
  --tcp-relay PUBLIC_ADDRESS:33445:PUBLIC_ID
```

The endpoint record is reachability input, not authority. IoTox neither enrolls it automatically nor
maintains a mutable community catalog.

### Backup and restore

Treat `key` and `PUBLIC_ID.txt` as one identity pair. Stop the unit, copy both to an encrypted
offline destination with mode 0600, then restart. To restore, stop the service, resolve the state
directory, install both files with its existing numeric owner/group and mode 0600, and start again.
For example, after independently validating that each backup is exactly 64 bytes:

```sh
sudo systemctl stop iotox-tox-bootstrap.service
state_dir=$(sudo readlink -f /var/lib/iotox-tox-bootstrap)
state_uid=$(sudo stat -c %u "$state_dir")
state_gid=$(sudo stat -c %g "$state_dir")
sudo install -o "$state_uid" -g "$state_gid" -m 0600 /offline/key "$state_dir/key"
sudo install -o "$state_uid" -g "$state_gid" -m 0600 \
  /offline/PUBLIC_ID.txt "$state_dir/PUBLIC_ID.txt"
sudo systemctl start iotox-tox-bootstrap.service
sudo grep -Ex '[0-9A-F]{64}' /var/lib/iotox-tox-bootstrap/PUBLIC_ID.txt
```

Do not run `DHT_bootstrap` directly from a source checkout: upstream writes `key` and
`PUBLIC_ID.txt` into its current directory. The NixOS unit supplies the private state directory.

Identity rotation is intentionally manual and disruptive. Withdraw the old published record first,
stop the unit, archive the old pair, remove both state files only after that review, and restart to
generate a new pair. Every consumer must then receive the new public record out of band. IoTox has
no operator key capable of performing this rotation remotely.

## Observe and maintain

Useful local checks are:

```sh
systemctl status iotox-tox-bootstrap.service
journalctl -u iotox-tox-bootstrap.service
ss -lntup | grep 33445
systemctl show iotox-tox-bootstrap.service \
  -p DynamicUser -p MemoryCurrent -p MemoryMax -p CPUUsageNSec -p CPUQuotaPerSecUSec -p TasksCurrent -p TasksMax
```

The unit uses an empty capability set, `NoNewPrivileges`, private devices/tmp, a read-only system,
restricted namespaces/address families, a 4096-descriptor ceiling, and explicit memory, CPU, and
task limits. These are blast-radius controls, not a bandwidth quota, DDoS defense, availability SLA,
or proof that the sample daemon is suitable for an unmonitored public host. Apply provider-side
traffic controls, patch cadence, abuse contact policy, and ordinary host monitoring separately.

For an update, keep the state pair backed up, rebuild from a reviewed IoTox commit, activate one
node at a time, and verify that the public identifier is unchanged after restart. Publish an outage
or endpoint removal through the same operator-chosen channel used to publish the record. Remove stale
listings before decommissioning. Contributions to upstream c-toxcore should go upstream; this module
does not create an IoTox-controlled forked network.

## Reproducible local gate

The flake check boots a NixOS VM, starts the exact pinned daemon, proves TCP and UDP listeners,
validates private state shape/modes, restarts the service, proves byte-identical identity retention,
checks configured cgroup ceilings and `DynamicUser`, and inspects the explicit firewall rules:

```sh
nix build .#checks.x86_64-linux.toxBootstrapServiceTest -L
```

This is a one-host KVM construction test. It does not prove public reachability, NAT traversal,
Internet abuse resistance, uptime, geographically independent capacity, relay fairness, or a
production support commitment. Those require operator deployment and independently retained
observations.
