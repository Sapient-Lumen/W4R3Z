# Debuggability-support session-scope boundaries — 2026-03-22

This note keeps **P-0486 Debuggability Support Contract Kit** from collapsing different debugging situations into one fake “debugging worked” claim.

## Keep these distinct

1. **broad support posture** — interactive, backtrace-only, crash-symbolication-only, weaker, or manual review;
2. **backend family observation** — GDB / LLDB / CDB / WinDbg / frontend route and version;
3. **session scope** — live local, remote target, attached process, containerized process, post-mortem core/minidump;
4. **capability witness** — which concrete user-facing tasks were demonstrated;
5. **claim ceiling** — what outward-facing claim survives after the narrower evidence is considered.

## What session scope is about

Session scope is specifically about the **shape of the debug subject** and how the debugger interacted with it.
Examples:
- opening a core file,
- attaching to a running process,
- launching a local binary,
- debugging over a remote stub,
- or inspecting a packaged bundle someone else captured.

## What session scope is not

- Not just artifact presence.
- Not just debugger-family coverage.
- Not a visualizer-compatibility matrix.
- Not a source-lookup/materials report.
- Not a replay debugger or async tracing product.

## Working rule for future passes

When future revisions touch **P-0486**, they must say explicitly whether the new work is about:
- posture,
- backend coverage,
- session scope,
- concrete capability witnesses,
- source-lookup materials,
- or claim ceilings.

Do not let the archive silently turn “we opened a core dump and saw a backtrace” into “interactive debugging works”, or “LLDB/Linux worked once” into “debugging support is broad”.
