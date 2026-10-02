# Sandwurm IoTox daemon replacement evidence — 2026-08-20

## Claim

Two concurrent IoTox NixOS guests under Sandwurm preserved a working relationship while the device
IoTox daemon was cleanly stopped and replaced from its existing savedata. Both virtual machines and
the controlled forced-TCP relay remained live. The stable client had to observe both the application
session and transport peer offline before the runner permitted replacement. Acceptance then required
the exact device Tox address, a fresh confirmed TCP session, a strictly advancing stable-client
online epoch, and fresh text in both directions.

This is the transport/application daemon-replacement slice of the two-node fault gate. It does not
claim Ratox PTY-incarnation survival, controller replay survival, link impairment, guest restart,
power-cut durability, synchronization, public-relay behavior, or production readiness.

## Accepted observation

The verified compact export is:

```text
.sandwurm/exports/pairs/pair.9i274oew
```

Both guests used IoTox `0.39.0 rev0039` and the pinned source-linked binary SHA-256:

```text
b5e58a4bb0e0d723f4e353f1faf8a0a49034b632225682efb7d35cab97c5408b
```

The relay was not restarted. The device daemon restarted exactly once from the same savedata. The
stable client recorded the complete offline transition and advanced from online epoch 1 to 2. The
new device process recorded its first process-local confirmed epoch as 1; that value is intentionally
not compared across process incarnations.

```text
route                              forced-tcp
scenario                           daemon-restart
device daemon restart count        1
bootstrap fixture restart count    0
device identity preserved          true
fresh confirmed replacement        true
client transport/session offline   true
client initial/recovered epoch      1 / 2
device initial/recovered epoch      1 / 1
final observed connection          tcp
post-restart text, both directions true
```

Digest bindings:

```text
client IoTox receipt   0d56c08b8a3e38a72aa7178c7cf628d3f9a5f12fd603453252414996606c7c7f
device IoTox receipt   7af486de74319e879d5fc7c8bf222563bbc89103e8205bce756933093e9387cb
client Sandwurm chain  20ab9967d57490250efa732ca6a2b309e802bff2d26963a6239834e85c6484dd
device Sandwurm chain  b4004c5860315ef6d44c19d6203130b35198414f602b2c6dbebfd907fd24f2f4
source manifest        c40a8704b7f6c7675185c84b49e1a59cc08d264ca93309eba8bd925ee85d34d6
```

Reverification command:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.9i274oew daemon-restart
```

The verifier rejects route/scenario disagreement, any relay restart, a device daemon restart count
other than one, either receipt failing to bind the preserved identity and fresh session, a missing
stable-client offline observation, or a stable-client epoch that fails to advance.

## Secret boundary

The original proof root retained writable private guest disks, detailed runtime state, reusable test
identity copies, and the bootstrap fixture secret key. The exporter omitted those classes, bound the
original manifest digest, copied only the verifier's seven-file allowlist, and reverified the 96 KiB
compact result before private-source cleanup. The compact export declares `contains_secrets=false`
and is the shareable evidence subset.
