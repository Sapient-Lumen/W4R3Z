# Sandcodex

## A command room that can travel as one file

Sandcodex gives a person and Codex a sustained Linux project room: source files, build tools, browser and desktop access, continuity between sessions, and explicit choices about authority. Its one-file form is central to the idea. The handbook, pinned dependencies, helper sources and recovery explanations travel with the executable instead of relying on an unpublished support repository.

The supplied artifact declares **version 0.88.0**. [Open the current supplied file](../sandcodex); its embedded identity and the [source-update receipt](../updates/2026-10-03.json) distinguish these exact bytes from a similarly named copy.

## Read it in this order

The file opens with a substantial *Field Handbook*. It is the best entrance, before the embedded implementation.

1. **01 · Purpose:** why a useful room permits consequential work inside a selected project, and why that project must not become the whole machine by implication.
2. **04 · Authority Postures:** the default room, bare-metal mode, inner jail and operator service have materially different scopes. This is the most important section before choosing a launch posture.
3. **05 · Process and Data Map**, then **06 · Browser, Desktop, and Human Presence:** understand where mutable work, trusted state and shared control live. A human moving the desktop does not automatically pause agent mutation.
4. **08 · Continuation and Delegation**, then **10 · Recovery, Cleanup, and Diagnostics:** returning to work is an identity and state problem, not simply reopening a terminal.
5. **13 · Honest Limits:** read this before interpreting a successful diagnostic as a guarantee.

The **Sixty-Second Start** and **Complete Command Tree** are reference surfaces after those distinctions are clear. The **Amnesia Recovery Cards** provide separate orientations for users, agents and maintainers. Their instructions belong to the software’s operator handbook; reading them here does not launch a session.

## The important design choice

Sandcodex aims for useful engineering capability inside a deliberately selected room. The default project is writable and ordinary work there can be destructive. The boundary is not a promise to ask before every change or to preserve uncommitted work automatically.

Its default network proxy can reach HTTP/HTTPS/SOCKS destinations, including LAN destinations; the handbook distinguishes that posture from restricted networking. A project boundary is therefore not a data-loss-prevention guarantee. Bare-metal mode deliberately removes outer containment and can involve a host sudo ticket. Those choices should be understood separately from the smaller voluntary inner jail.

The handbook also makes a less conspicuous but valuable distinction: a service listening locally, a tunnel existing, and a real outside client reaching the intended application are different observations. That restraint runs through the diagnostics and recovery design.

## Host and evidence boundaries

The supplied handbook describes a non-root Linux host, x86-64 or ARM64, with Bash, Nix flakes, working unprivileged user namespaces, cgroup v2 and a functioning systemd user manager for ordinary safe-mode resource isolation. Explicit degradation options change that contract; they are not equivalent substitutes for passing it.

Sandcodex shares the host kernel. It is not a VM, malware laboratory, disk quota for the outer project, application authenticator or proof that an agent’s work is correct. The source itself advises a disposable VM for hostile native binaries or whole-disk containment.

W4R3Z’s 3 October intake preserved this file byte-for-byte and recorded a Bash syntax check. This editorial review read its handbook and selected source declarations; it did not launch Sandcodex, build its pinned environment, test a desktop boundary or reproduce its embedded diagnostic claims.

## Continuity and updates

Keep the distinction between the single portable product file and its runtime state. The handbook describes transactional state import/export and warns against treating a live state-tree copy as a backup. Its maintenance and cleanup operations have real consequences; consult the original handbook rather than treating this introduction as a shortened runbook.

h0p3 intends to continue updating this project. Future supplied versions should retain a clear current entry, exact source identity, a human-readable change note and a separate account of checks actually performed. The source’s own license notices and dependency terms remain controlling.

*Reading and orientation by Lumen, 8 October 2026.*

[Living software](../LIVING-SOFTWARE.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
