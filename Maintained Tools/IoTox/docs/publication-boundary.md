# Public publication boundary

Status: current seed-publication posture.

This repository is intended to be publishable as an IoTox source seed. It keeps
the technical evidence needed to understand the project, but it should not
publish avoidable founder-host personal paths.

## Personal paths

Absolute host paths that named the founding operator's home directory were not
intended as public provenance. The public tree uses portable placeholders or
portable relative inputs instead:

- the Sandwurm flake input is `git+file:../sandwurm`;
- Sandwurm command examples use `SANDWURM_ROOT`;
- discarded host Trash paths use `$XDG_DATA_HOME/Trash/files`;
- workspace-local evidence paths use repository-relative or placeholder roots.
- public standalone binaries use portable `doctor binary` provenance labels
  such as `source-snapshot` and `standalone-build` instead of absolute
  founder-host build paths, and the standalone build path-scrubs dependency
  source file names while suppressing local build RPATHs.

Generic examples and fixtures such as `/home/alice/...`, `/home/USER/...`,
`/home/operator/...`, and the Sandworm sandbox's own `.sandworm/home/...` or
`/run/sandworm/home/...` paths are not founder-host disclosures.

## Laboratory topology

The Sandwurm two-node laboratory description is intentionally public
reproducibility information. It describes a same-host VM qualification topology:
two sibling IoTox NixOS guests, controlled bootstrap/relay roles, prepared
TAP/NAT substrate, Cloud Hypervisor tooling, and cgroup/kernel qualification
scope. Those records describe the founding lab, not a private deployment, and
they are part of the evidence boundary.

The topology should stay specific enough that another operator can understand
what was actually tested. It should not be rewritten into a vague claim that
would make the evidence look broader than it is.

## Historical operational records

Dated evidence, generated run identifiers, compact proof names, resource
measurements, and cleanup history are intentionally retained when they explain
what was built or why a claim is scoped. They are engineering provenance, not
user data. When they mention host organization, the public form should prefer
portable names over personal absolute paths.

This transparency is bounded: the seed package should still exclude mutable
runtime state, private keys, RecallRoot phrases, `.toxsave` files, personal
absolute host paths, and unrelated ignored workspaces.

Publication review should inspect both text files and shipped binary strings
for founder-host paths. Generic examples and sandbox-internal paths are allowed;
absolute paths naming the founder's host workspace are not.

## Publisher note

The public seed is allowed to preserve tests, architecture, threat models,
public fixture addresses, public keys, hashes, and security-control
documentation. A credential-pattern scan finding no private-key PEM headers,
GitHub token patterns, or AWS access-key-ID patterns is consistent with the
intended boundary, but it is not a substitute for the datacube verifier and
publisher review.
