# Environment capability contract — rev0084

The cube repeatedly said native GTK validation was unavailable, but that claim
was previously prose rather than executable authority. Rev0084 adds:

```text
data/current_environment_capability_contract.json
tools/audit_current_environment_capabilities.py
data/rev0084_environment_capability_audit.json
```

The audit probes Python `gi`, GTK3, GTK4, Gio, Xvfb, D-Bus session tooling,
`msgfmt`, and native Win32 availability. It then cross-checks packet
`missing_evidence` and ensures no Search Again candidate is selected while its
required native integration evidence is absent.

The policy distinction is deliberate:

```text
capability available   != native scenario validated
capability unavailable != product behavior disproved
model/source test       != native UI test
```

Observed in this cloudtainer:

- `gi`, GTK3, GTK4, and Gio imports: unavailable;
- Xvfb and `dbus-run-session`: available;
- `msgfmt`: unavailable;
- native Win32: unavailable on this Linux host.

This turns an environmental limitation into a checked scope boundary and avoids
repeatedly overstating source/model evidence as UI validation.
