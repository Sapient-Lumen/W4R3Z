# Oblivious sandboxing launchers (Capsicum adoption without footguns)

Capsicum’s security win is simple: **acquire resources up front**, then enter capability mode (`cap_enter(2)`) and operate only on already-held capabilities.

In practice, teams fail to adopt Capsicum because “acquire everything up front” is hard:
- dynamic linking needs library opens
- plugins/NSS/CA roots often imply late file opens
- shell-outs expect PATH lookups
- config discovery is often path-driven

If we don’t ship a **repeatable** pattern, people keep ambient authority “just to make it work”.

DeriveBSD can make this a solved problem by providing an *oblivious sandboxing* launcher as a first-class runtime primitive.

## DeriveBSD target

A tiny launcher that:
- opens **exactly** the directories/files/sockets a program is allowed to use
- reduces rights on those descriptors (Capsicum rights masks)
- populates a stable *preopen map* for the child (directory FDs + labels)
- (optionally) performs initial dynamic linking with pre-opened library dirs
- enters capability mode, then `execve()` (or jumps to the already-linked program)

Key property:

> Capability mode becomes the default, not the heroic option.

## Design sketch

### 1) A hashable `preopen.map` object

A typed manifest (built by activation planning) describing:
- labeled directory capabilities (e.g., `cfg_ro`, `state_rw`, `logs_append`, `lib_ro`)
- per-label rights masks (read, write, fstat, ioctl allowlist, etc)
- any “well-known file” handles (e.g., a specific CA bundle FD)
- optional broker endpoints (Casper services / portals)

This should be recorded as evidence so `derive explain` can answer:
- what *ambient authority* was removed
- what handles were granted instead
- what policy decision produced those grants

Schema: `spec/preopen.map.schema.json`
Example: `spec/examples/preopen.map.json`

When the map changes between generations, attach a compact posture diff to drift bundles:
See: `docs/453-preopen-map-diff-as-review-surface.md`.

### 2) Runtime pattern: **openat-first**

DeriveBSD-managed daemons should treat directory FDs as the primary capability:
- “open file X under directory Y” → `openat(dirfd, "X", ...)`
- no absolute paths after `cap_enter`

This aligns with how Capsicum intends new resources to be derived from existing capabilities.

### 3) Dynamic linking: make it boring

We already document the underlying constraints (`docs/180-capability-mode-dynamic-linking.md`).
The launcher should standardize the solution:
- pre-open library directories and pass them as capabilities
- optionally pin a known runtime linker + library closure for the daemon
- forbid late `dlopen()` by default; require a broker/portal exception

### 4) Tooling interface

Proposed UX surface:
- `derive run --profile <promise-profile> -- <cmd>`
- `derive svc start <name>` always uses the launcher (no “naked exec”)

Where `<promise-profile>` compiles into:
- jail knobs (where applicable)
- mount views (`mount.view`)
- preopen maps (`preopen.map`)
- optional broker endpoints (Casper/portal routing)

## Why this is worth baking in

- It turns a *security primitive* (Capsicum) into a **product default**.
- It reduces policy review to a single artifact (profiles → preopen/mount/brokers).
- It makes “late authority” visible: any broker request produces receipts.

## References

- Capsicum overview (capability mode; rights on descriptors): https://man.freebsd.org/cgi/man.cgi?query=capsicum&sektion=4
- `cap_enter(2)` (enter capability mode): https://man.freebsd.org/cgi/man.cgi?query=cap_enter&sektion=2
- `cap_rights_limit(2)` (rights masks on descriptors): https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2
- “Towards oblivious sandboxing with Capsicum” (preopen maps + practical adoption patterns): https://www.engr.mun.ca/~anderson/publications/2017/towards-oblivious-sandboxing.pdf
- vBSDCon slides variant (Capsh/libpreopen concept): https://papers.freebsd.org/2017/vbsdcon/anderson-Towards_Oblivious_SandBoxing.files/anderson-Towards_Oblivious_SandBoxing.pdf

Related:
- Portals/powerbox framing: `docs/179-portals-and-powerbox.md`
- Capability-mode dynamic linking guidance: `docs/180-capability-mode-dynamic-linking.md`
- Capsicum/Casper hardening plan: `docs/49-capsicum-casper-hardening.md`

Last updated: 2026-02-28r175
