# Genuine-peer TCP-only evidence — 2026-08-14

Classification: redacted shareable report. Disposable profiles, secrets, ledgers, stores, runtime
trees, and logs were destroyed by the harness.

## Inputs

```text
source-commit=89b0a59
dependencies-lock-sha256=fa7b36c0f2de857ed35cb63967ab29fcdd6fa874ae5c4c0efe572f0195930e86
standalone-binary-sha256=7801cacb9153968e8a96daf278d00abfa83a13e05fb557766c3d4a82745deb2b
provider=c-toxcore-0.2.23 source-linked
route=tox/native TCP-only using the pinned default TCP-relay catalog
udp=disabled
local-discovery=disabled
dht-announcements=disabled
hole-punching=disabled
timeout-seconds=240
```

The exact provider-ABI test independently verifies that TCP-only configuration passes zero to all
four c-toxcore option setters. The genuine run then exercised the whole lifecycle with that mode.

## Redacted result

```text
real-peer-smoke=pass
peer-a-public-key-sha256=489b8ade2e5d72b073eb9cacd19319fdf316d03e79b7efbeb18b9a56e09a09e3
peer-b-public-key-sha256=17918e72645379f6f92037fd607e1481b55ddfbd25e50e472c6a993e76ad4a0f
transport-mode=tcp-only
session=canonical-hello-transcript-confirmed-both-directions
authority=stable-principal-proof-and-read-telemetry-grant-both-directions
message=delivered-to-peer-journal
command=device.describe-received-succeeded-and-durably-reloaded
summary=system.summary-received-succeeded-and-typed
file=finite-exact-bytes-completed
friendship=removed-both-directions-and-readded-with-fresh-session-proof
restart-identity=tox-and-stable-device-preserved
```

## Claim boundary

This is relay-only evidence for the named run and catalog, not proof about every relay, censorship
environment, proxy, or network failure. Controlled loss, rapid reconnect, resource measurements,
and cross-client compatibility remain open M3 work.

## Measured reconnect rerun

Harness commit `e921ea2` added a real peer-process outage and bounded host measurements. The same
source-linked binary passed the expanded TCP-only lifecycle:

```text
peer-a-public-key-sha256=eb40137a28585139a32e61e90bf5d1c51262788b1282e4e9ce0943d4bdaf55b0
peer-b-public-key-sha256=b7eafd84f940bf939f1febd63908eb6b380a6e336381986e9767181e29085302
reconnect=process-restart-fresh-session-and-authority-proof
initial-convergence-ms=64178
reconnect-convergence-ms=76473
peer-a-rss-kib=8260
peer-b-rss-kib=8672
peer-a-cpu-ticks=941
peer-b-cpu-ticks=74
peer-a-context-switches=10414
peer-b-context-switches=5602
peer-a-open-fds=34
peer-b-open-fds=34
protocol-journal-bytes-proxy=12402
persistent-tox-savedata-bytes=6402
```

CPU ticks and context switches are cumulative process observations at the sample point. Protocol
journal bytes are only an application-frame proxy, not a wire-traffic measurement. These values
are a baseline from one run, not yet acceptance budgets.
