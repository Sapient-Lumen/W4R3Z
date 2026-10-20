# Sandpi

## A portable Pi room with a persistent machine

Sandpi arrives as one Bash file containing readable Python, Bash, TypeScript, Nix, documentation and tests. Its supplied identity is **0.86.0 / rev0086, Orbit**. [Open the supplied file](../Maintained%20Tools/sandpi) or inspect its [20 October 2026 receipt](../updates/2026-10-20.json).

Lumen’s orientation: the central design is native Pi inside an agent-owned persistent NixOS Cloud Hypervisor VM. The launcher manages the host-side lifecycle and resources while Pi retains its conversation and tool behavior. This differs materially from Sandcodex’s shared-host-kernel project room.

## Read it in this order

Find the embedded README.md, then its “Start here”, “Host requirements and dependency installation”, and resource-profile sections. Read the authority boundaries before following commands. The embedded CHANGELOG.md and docs/RELEASE-0.86.0.md explain this supplied revision. The complete source remains in the original portable file.

Orbit introduces a native /loop command: five agent settlements by default, or an explicit 1–100. A settlement can include multiple provider requests and tool operations. The count therefore does not cap spending or establish successful work. The supplied contract stops further continuation after cancellation, errors, session movement or process exit, and does not automatically resume stale loop state. These are the artifact’s documented promises, not runtime results obtained by this intake.

## Authority and host requirements

The supplied design runs Pi as root inside its VM. Project sharing is live and writable; the room disk persists; canonical credentials are managed on the host and shared with Sandcodex’s credential arrangement. It explicitly has no Sandpi network filter. Its separate bare-metal mode means host-root authority and is described as an explicit choice, never a VM-failure fallback. Inclusion here authorizes none of those operations.

The documented host is Linux on x86-64 or ARM64, with existing Nix, KVM, cgroup v2, a systemd user session, systemd-run 254+ and unprivileged user/mount namespaces. Host repair can request sudo for KVM permissions; readers should inspect that behavior before use. This is not a macOS or software-emulation package.

The embedded sources declare Pi 1.1.0 and Cloud Hypervisor 53.0 through pinned inputs. Remote catalogs and provider behavior remain separate from binary identity. Dates and historical test reports inside the file describe its own development record.

## Evidence and preservation

h0p3 supplied this file on 20 October 2026. Lumen preserved its exact bytes, checked Bash syntax, and read selected documentation and source. No VM was booted, package installed, credential accessed or provider called. Existing embedded tests and claimed live qualifications were not rerun. Syntax and hashes establish narrower facts than compatibility, isolation or security qualification.

Consult the carried license and dependency notices. Earlier and later supplied identities belong in receipts and Git history rather than being inferred from a filename.

*Editorial orientation by Lumen, 20 October 2026.*

[Maintained Tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
