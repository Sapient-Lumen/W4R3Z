# Linux split-DWARF sidecar scenario

This scenario keeps the crate honest about Linux debug layouts:

- debug info exists, but not purely as one embedded story,
- sidecars are part of the support contract,
- and the bundle should preserve that mapping instead of flattening everything into “Linux release binary”.
