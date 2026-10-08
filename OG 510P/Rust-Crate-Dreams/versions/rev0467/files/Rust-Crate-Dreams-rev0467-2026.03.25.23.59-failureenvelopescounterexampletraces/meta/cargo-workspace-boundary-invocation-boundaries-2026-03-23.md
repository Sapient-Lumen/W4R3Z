# Lane boundaries — P-0506 Cargo Workspace Boundary Doctor Kit (2026-03-23)

When future revisions touch **P-0506** or nearby Cargo/discovery lanes, do not let the archive collapse these into one fake “workspace boundary support” story:

1. **ancestor discovery** — which parent candidates existed and where observation stopped;
2. **config layering** — file layers, include edges, env overrides, CLI overrides, and path bases;
3. **invocation mode** — cwd auto-discovery, `--manifest-path`, manifest-command mode, and single-file package mode;
4. **membership diagnosis** — root/member/excluded/ambiguous package classification;
5. **advice** — workaround vs repo cleanup vs upstream design gap.

Do not let any of the following stand in for an honest answer:
- “we used `--manifest-path`,”
- “there was a `.cargo/config.toml`,”
- “Cargo found the workspace root,”
- “the script used `foo.rs`,”
- or “the error message mentions a parent manifest.”

A bundle can contain all of those facts and still fail to say:
- which ancestor candidates were actually in play,
- how config layering and path bases worked,
- or whether workspace auto-discovery was even available in that invocation mode.
