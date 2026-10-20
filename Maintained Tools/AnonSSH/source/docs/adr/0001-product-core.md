# 0001: Keep the product core direct

Status: superseded by [0002](0002-bond-is-product-core.md)

AnonSSH is one Rust executable with direct SAM, Tor control/SOCKS, OpenSSH, and
Dropbear integration. The Nix package supplies those external runtimes. The Bash file
is only a build-and-exec convenience wrapper.

Simulation, campaign orchestration, evidence scoring, dashboards, and an unproven bond
protocol did not belong in the product core. That constraint protected the direct
recovery path until its transports were proven. ADR 0002 changes the product boundary
now that striping has an explicit protocol and test plan.
