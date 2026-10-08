# Tauri dev joins frontend devserver and Rust reload without flattening them

This scenario exists to force **P-0537** to keep adjacent iteration routes separate.

Tauri documents `tauri dev` as development mode with hot-reloading for Rust code while also using `build.devUrl` and `beforeDevCommand`, which usually starts a frontend dev server.
A serious support bundle must not rewrite that composite flow into one simple state or latency claim.
