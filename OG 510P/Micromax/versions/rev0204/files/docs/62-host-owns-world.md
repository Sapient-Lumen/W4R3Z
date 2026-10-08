# Host Owns the World (embedding contract)

Micromax is intended to be **embedded** (first big target: a terminal text editor).
To keep the VM small, debuggable, and safe, we assume:

## Principle: micromax is sandboxable; side effects are host-mediated

- Micromax core is small and deterministic.
- All “real world” side effects happen through **explicit hostcalls**.
- Hostcalls are **allowlisted** and can be **capability-gated** later.

This mirrors how many embeddable languages treat the host boundary as part of the design surface.
For example, FICL (“Forth Inspired Command Language”) was designed to be embedded and used as a
command/macro language inside larger programs:
https://ficl.sourceforge.net/ficl.html

And modern embedded languages like Janet explicitly document embedding as a core use-case:
https://janet-lang.org/capi/embedding.html

## Versioning and feature detection

Even in early stages, a plugin ecosystem needs a stable handshake:

- `host.api-version` returns a version string (e.g., `"0.1"`)
- `host.feature?` checks for optional features (filesystem, job system, UI hooks, etc.)
- `host.features` returns a list
- `host.capabilities` can optionally return a small registry with descriptions (rev78)

The host should also expose a *minimum* set of features for good ergonomics:
- printing/logging
- error reporting
- a clock/time source (optional)
- file access (if allowed)

## Budgeted execution

To avoid “plugins freeze the UI”, the host should:
- run plugin callbacks under `catch`
- set a step budget (or time budget) per callback
- handle budget exceed as a controlled error

## Two contexts (planned)

We plan to distinguish:
- UI callback context (fast, budgeted, allowed to mutate editor state)
- background job context (heavier work, cannot mutate UI directly; communicates via messages)

We haven’t implemented jobs yet; this doc is the contract shape.

## No direct host memory (recommended pattern)

A useful safety rule for embedded Forth-like runtimes is:

> The VM never gets raw pointers into host memory.

Instead, the VM operates on **VM-owned memory** (or opaque handles) and the host provides
explicit operations (hostcalls) that can validate boundaries and capabilities.

This is the same broad pattern used by tiny embeddable Forths like **zForth**, which
explicitly abstracts VM memory to allow proper boundary checking instead of exposing
host memory directly.

In Micromax this means:
- keep `@`/`!` operating on VM cells (not host addresses)
- represent editor resources as *names* or opaque handles (buffer name, timer id, etc.)
- expose higher-level hostcalls for sensitive operations (fs, jobs, ui)
- gate optional/unsafe features behind `host.feature?` checks

See also: `plugins/capdemo/` for a minimal capability-checking example plugin.
