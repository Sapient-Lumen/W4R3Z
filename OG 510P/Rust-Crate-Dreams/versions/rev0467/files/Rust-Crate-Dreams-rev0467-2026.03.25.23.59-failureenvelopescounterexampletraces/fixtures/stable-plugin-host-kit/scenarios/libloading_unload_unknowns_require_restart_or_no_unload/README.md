# libloading unload unknowns require explicit lifecycle posture

This scenario captures a host built on dynamic loading substrate where unload safety is **not** proved.
The important truth is that load success does not imply safe unload or true hot reload.

What the receipt should prove:

- load is explicit and on-demand,
- unload is `unsupported` or at best `process_restart_only`,
- and any replacement flow must be labeled accordingly.
