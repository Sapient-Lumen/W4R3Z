# Ratox restart-fence process evidence — 2026-08-17

Scope: deterministic Linux process boundary for rev0020.

Executable gate:

```text
iotox.ratox-restart-fence-process
```

The test launches the shipped `iotox` executable against the exact shared-library c-toxcore double
with a valid owner-private profile store. It proves:

```text
first daemon reaches phase=running with a nonzero held incarnation lease
committed record is exactly 128 bytes with IOTXRIN1 magic, value, and complement
second process sharing identity plus restart lane exits 3 on explicit lease contention
failed contender publishes phase=failed and lease-held=0
failed contender does not advance the committed record
orderly first-daemon shutdown publishes phase=stopped and releases the lease
successor reaches running and commits exactly first-incarnation + 1
successor status and committed record agree
```

The fixture uses separate runtime roots, tox savedata paths, command stores, and logs for each
process, so the shared device identity, authority ledger, and incarnation lane are the intended
contention boundary. Unit tests provide cryptographic and hostile-path detail not duplicated here.

This is not genuine Tox network, two-host, storage power-cut, or restart-persistent PTY evidence.
