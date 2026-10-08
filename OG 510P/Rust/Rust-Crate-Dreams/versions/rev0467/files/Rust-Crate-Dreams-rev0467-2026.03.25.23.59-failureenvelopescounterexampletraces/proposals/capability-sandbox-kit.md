---
id: P-0074
title: Capability Sandbox Kit — cross-platform “least privilege” for Rust processes
status: idea
domains: [security, sandboxing, os, linux, macos, windows]
last_reviewed: 2026-03-04
evidence:
  - https://docs.kernel.org/userspace-api/landlock.html
  - https://users.rust-lang.org/t/using-rust-programs-inside-seccomp-sandbox/18488
  - https://www.chromium.org/developers/design-documents/sandbox/osx-sandboxing-design/
needs:
  - Make it easy to sandbox helpers/parsers against untrusted inputs.
  - Provide a single capability model that can map to platform primitives.
risks:
  - “Lowest common denominator” APIs that are too weak to matter.
  - Platform complexity (App Sandbox, Windows restricted tokens, etc).
---

## Problem

Rust is memory-safe, but real systems still process adversarial inputs. Developers want defense-in-depth: sandboxing a subprocess or component with tight access to system resources. Today, this is fragmented:

- Landlock’s goal is to restrict ambient rights and help mitigate the security impact of bugs or malicious behaviors.  
  Source: https://docs.kernel.org/userspace-api/landlock.html
- Rust devs hit pragmatic seccomp footguns (unexpected syscalls from std causing violations).  
  Source: https://users.rust-lang.org/t/using-rust-programs-inside-seccomp-sandbox/18488
- macOS sandboxing is powerful but complex; Chromium documents a dedicated macOS sandbox architecture.  
  Source: https://www.chromium.org/developers/design-documents/sandbox/osx-sandboxing-design/

## Design goals

- A **unified capability policy** (Rust builder + optional declarative file):
  - filesystem rules (read/write/exec)
  - network (deny/allow; honest “best-effort” mapping)
  - process + IPC rules
  - resource limits (cpu/mem/fds)
- Multi-backend:
  - Linux: Landlock + optional seccomp profiles
  - macOS: App Sandbox where realistic; documented constraints
  - Windows: job objects + restricted tokens

## API sketch

```rust
pub struct Policy { /* fs/net/syscalls/resources */ }

pub trait Backend {
  fn spawn_sandboxed(&self, policy: &Policy, cmd: &Command) -> Result<Child>;
}
```

Include a `policy doctor` CLI that explains enforced vs ignored rules per platform.

## Milestones

- 0.1: Linux Landlock FS sandbox + spawn helper + testkit
- 0.2: seccomp integration + syscall profile generator
- 0.3: Windows backend
- 0.4: macOS backend + deployment guidance
- 1.0: stable policy format + conformance suite

## Sources

- https://docs.kernel.org/userspace-api/landlock.html
- https://users.rust-lang.org/t/using-rust-programs-inside-seccomp-sandbox/18488
- https://www.chromium.org/developers/design-documents/sandbox/osx-sandboxing-design/
