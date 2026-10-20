# Ratox cgroup kernel qualification

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Decision: ADR 0327
- Status: NixOS KVM gate accepted

## Direct gate

```sh
nix build .#checks.x86_64-linux.ratox-cgroup-vm -L
```

The accepted output is
`/nix/store/8yssjglgwhs8f943xjk8sjj9qn2x1gka-vm-test-run-iotox-ratox-cgroup`.
The source-linked harness IoTox SHA-256 is
`63fc8acf4c54ad037c2824fbd36d5814ddf13acd709e0310369e45b1b23ff07e`; the cgroup process-oracle
driver SHA-256 is
`5a0f6b20e756465b9f659521cad2ec134ba6bc12eced7e4c38364b1119128648`.

One x86_64 KVM guest booted NixOS on Linux 6.6.94 with `psi=1`, cgroup v2, and systemd transient
services using `Delegate=yes`. The VM required readable host PSI files plus `cpu`, `memory`, and
`io` controllers, then ran five separate delegated services:

- `--lifecycle`;
- `--memory-resource`;
- `--cpu-resource`;
- `--io-resource`;
- `--pressure-admission`.

All five services exited cleanly. The NixOS test script completed in 14.73 seconds after boot. The
memory route logged an expected pids-controller rejection from the kernel, and the I/O route reported
3 MiB written to disk from systemd's service accounting.

## Findings captured

Fresh cgroup namespaces in a delegated systemd service may expose controllers without preactivating
them. The process oracle now moves itself into a sibling anchor leaf before enabling the controller
set, preserving cgroup-v2's no-internal-process rule while exercising the exact private subtree used
by production `SessionCgroup` setup.

The VM also exposed a kernel `io.stat` shape that a synthetic parser fixture did not cover: a
zero-accounting device line can be emitted as only the device key or as the device key plus a final
space. IoTox now accepts those as zero evidence and still requires complete read/write tuples once a
nonempty keyed line is present.

Disabling `cgroup.pressure` remains fail-closed on live admission. For a new admission object, this
kernel withdraws per-cgroup pressure files after the disable, so startup may fail as `unsupported`
while opening `cpu.pressure` rather than as `unavailable` while reading `cgroup.pressure=0`. The
oracle now requires startup failure and permits either exact fail-closed class.

## Evidence boundary

This is a real Linux kernel plus real systemd delegated-service qualification, but it is still one VM
kernel and one service-manager configuration. It does not prove physical hardware behavior, every
distribution's cgroup delegation policy, hostile root or same-UID cgroup managers, parent CPU/IO
contention, PSI trigger latency under live pressure, long-duration leaks, Tox traversal, or Ratox
production activation.
