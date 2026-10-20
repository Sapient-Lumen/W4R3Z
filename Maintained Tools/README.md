# Maintained Tools

Five projects maintained by **h0p3**, with introductions and catalog organization by **Lumen**. Start with the job you want to do; follow each introduction for requirements and limitations.

- **Code with Codex on Linux:** Sandcodex.
- **Run the Pi coding agent in its own persistent VM:** Sandpi.
- **Keep ChatGPT working on a project over successive rounds:** qomrade.
- **Connect your devices for commands and folder sync:** IoTox.
- **Configure NixOS and review proposed system changes:** Monsternix.

These are different tools, not five parts you must install together. The single-file launchers and userscript are linked below; IoTox is a source tree. Nothing on this page is an installation instruction.

## IoTox

Send authorized commands and synchronize folders between your devices over Tox, including tracking work across interruptions. For people exploring self-managed device access. The supplied security policy warns against using it to protect production devices or secrets.

- [Introduction and provenance](IoTox/W4R3Z.md)
- [Project files and documentation](IoTox/)

## Monsternix

Configure a NixOS system and review evidence for a proposed configuration before accepting it. For NixOS operators collaborating on system changes. The supplied module requires machine-specific configuration through a machine adapter. Its source includes explicitly opt-in experimental vault and encrypted keystroke-journal facilities; their presence is not permission to enable them.

- [Read the Monsternix introduction](../guides/Monsternix.md)
- [Current supplied configuration.nix](configuration.nix)
- [3 October 2026 source-update receipt](../updates/2026-10-03.json)

## Sandcodex

Give Codex a selected Linux project directory, build tools, and browser/desktop access for hands-on coding. For Linux users working on repositories with an agent. It shares the host kernel; it is not a VM.

- [Read the Sandcodex introduction](../guides/Sandcodex.md)
- [Current supplied sandcodex file](sandcodex)
- [20 October 2026 source-update receipt](../updates/2026-10-20.json)

## Sandpi

Run the Pi coding agent in a NixOS virtual machine whose disk persists between sessions. For Linux users with Nix and KVM who want an agent in its own OS environment. Pi means the coding agent, not Raspberry Pi; shared project files remain writable.

- [Read the Sandpi introduction](../guides/Sandpi.md)
- [Current supplied sandpi file](sandpi)
- [20 October 2026 source-update receipt](../updates/2026-10-20.json)

## qomrade

Keep ChatGPT working through successive rounds of research, writing or development without manually sending every continuation. It supports background work, model selection, recovery, and optional downloads of generated files. For people developing a substantial project over many turns, not just asking a one-off question. Requires a userscript manager; progress and correctness still need review.

- [Read the qomrade introduction](../guides/qomrade.md)
- [Current supplied qomrade.user.js](qomrade.user.js)
- [20 October 2026 source-update receipt](../updates/2026-10-20.json)

## What “current” means here

It means the current supplied copy in W4R3Z, not a claim that this repository follows every upstream release automatically. Sandcodex and Sandpi retain the byte-for-byte files supplied on 20 October 2026; both received Bash syntax checks and bounded source review, without launch or installation. Monsternix retains its 3 October supplied copy and bounded source review. IoTox’s own introduction records its separate provenance and checks.

Continued maintenance is distinct from compatibility, runtime testing and security qualification. Read each project’s setup requirements, risks and license before use. The source-update receipt and Git history retain earlier identities.

[Whole catalog](../CATALOG.md) · [The prose library](../OG%20510P/README.md) · [W4R3Z](../README.md)
