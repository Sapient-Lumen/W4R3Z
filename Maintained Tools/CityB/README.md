# CityB

CityB is a toolkit for distributing a shared, governed record across unreliable routes. Its central distinction is that a carrier can help someone discover candidate bytes, but cannot make those bytes authoritative. A node must evaluate the archive and its signatures against the relevant rules before adopting a state. That separation lets a URL, file host or offline handoff carry a lead without becoming the council that decides what is valid.

The operator kit brings three roles together:

- **cityb** is the operator workbench for preparing and reviewing work, managing archives and coordinating the workflow.
- **cityb-node** is a small field receiver and verification node, with a bounded correspondence role.
- **cityb-biggun** is the heavier development, measurement and exercise tool.

They share a Rust workspace and protocol material. The kit includes the corresponding source, documentation and fixtures, so a recipient can inspect the design and continue developing it. The carried current-state briefing distinguishes implemented workflows from research and future plans; it is a useful first stop after the kit's `START-HERE.md`.

## Download

- [CityB 0.1.0 Linux x86-64 operator kit](CityB-operator-kit-0.1.0-x86_64-linux-unsigned-revised.zip) · [SHA-256 checksums](CityB-0.1.0-SHA256SUMS)

This distribution kit is **unsigned**. Its checksums help detect changed bytes, but they do not authenticate the publisher. That is a separate question from the signed governance archives CityB is designed to evaluate. The ZIP and both included checksum manifests were verified for this release; the programs were not executed as part of this update.

The standalone CityB product is distinct from the vaulted CityB of ChatGPT artwork in [/b/](../../b/README.md).
