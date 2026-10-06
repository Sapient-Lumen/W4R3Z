# RFC-0083: Compartmentalized control planes

Status: Draft

## Summary

Allow (optionally) splitting privileged control-plane subsystems into separate jails/microVMs:
- networking domain
- firewall/policy enforcement domain
- fetch domain
- publish/signing domain

Reference model: Qubes OS firewall chaining and isolation of network-facing domains. https://doc.qubes-os.org/en/latest/user/security-in-qubes/firewall.html

## Goals

- Reduce blast radius of compromises in network-exposed components.
- Preserve policy enforcement even if a network service domain is compromised.

## Design sketch

- Define control-plane roles and their minimal privileges.
- Express role composition in Plan.
- Bind role placement and permissions into the runtime blast radius contract.

See: `docs/115-compartmentalized-control-planes.md`.
