# unstable_module_leak_quarantine

The tool mostly uses `rustc_public`, but one code path touched semver-exempt bridge surfaces.
The point is to classify that result as **quarantined**, not silently compatible.
