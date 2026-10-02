# 2026-09-26 terminal evidence collector smoke

This note records the first native `iotox evidence collect terminal` smoke on
the local workstation. The proof bundle is ignored workspace state:

```text
.sandwurm/exports/manual-terminal-evidence-smoke/
```

The command wrote 11 content-free terminal stable receipts and intentionally
stayed blocked because no real 24-hour terminal long-soak receipt was present:

```text
iotox-evidence-collect-terminal-v1
root=/tmp/iotox-daily
peer=alias:self
accepted-terminal-stable-gates=11/12
stable-manifest=blocked
missing=long-soak
boundary=terminal-long-soak-must-be-real-24h-receipt; operator-labels-are-content-free-host-route-evidence
```

`iotox evidence manifest ... --scope terminal` then failed closed with:

```text
unable to open terminal.long-soak: No such file or directory
```

That is the intended line. The 11 operator-attested gates are now ordinary
native receipts. Stable terminal shipping still requires a real elapsed
`iotox.terminal-long-soak-receipt.v1` accepted at the 86,400-second floor.

The long-soak plan for this local root/peer is:

```text
iotox terminal soak-plan --root /tmp/iotox-daily --peer alias:self --seconds 86400 --sample-every 300
receipt-command=iotox terminal soak-receipt --root /tmp/iotox-daily --peer alias:self --route native --required-seconds 86400 --observed-seconds OBSERVED_SECONDS --samples SAMPLES --max-sample-gap-seconds MAX_GAP_SECONDS --reconnect-attempts RECONNECT_ATTEMPTS --session-generations SESSION_GENERATIONS --failures 0 --result accepted --label terminal.24h
verify-command=iotox terminal soak-verify RECEIPT --minimum-seconds 86400
```

Retained receipt hashes for the 11 non-soak gates:

```text
terminal-activation-decision.receipt sha256=2ac72bd0d78116796b66cbe7ecee99047ce34696007e1bb571bbe44aba45b961
terminal-cgroup-delegation.receipt sha256=2d34e7d00ebdd69c9b90b5c7c8de430a253e1fc3f39494ad0079dbe5113c10e5
terminal-daily-control.receipt sha256=d30090f8a136cd97fe6ae12722e660c2a0e8daab4bc9011b3e79c670cdaf2583
terminal-i2p-route-loss.receipt sha256=33e3dc65450e4a905e019210ac964120e384dbcdce936f3decefde6012d417d6
terminal-profile-freshness.receipt sha256=02515607d48b4be158e8d663fc6ac805f20eab557638511b20c7e7be69a6ec78
terminal-reconnect-continuity.receipt sha256=343fb8a452dad5492bcdc46a8a07c9d77d1574693341a494459d06787cf55cb0
terminal-route-loss.receipt sha256=651c2a52189692ec736a469bfcf69622380c6d5076ef82db6aea469c7db7722d
terminal-security-review.receipt sha256=c14865e34e5dcf4bd7efff5428d8fe7ab715aab2ed973d79b8174a6c4b042ce8
terminal-service-supervision.receipt sha256=243350d13f5361ceb25646301b3ae2d63b9ecc43c0e19023da0771d94e5f9803
terminal-sudo-policy.receipt sha256=4dbc6db5bf278ec424f00c95fb59dffada7ddb39b8d94c626ff8364bdaee7e91
terminal-tor-route-loss.receipt sha256=1417d0e70593adae3302f4315974ea5dcddcb6397eab9c1d5657659e9a24d3d2
```

