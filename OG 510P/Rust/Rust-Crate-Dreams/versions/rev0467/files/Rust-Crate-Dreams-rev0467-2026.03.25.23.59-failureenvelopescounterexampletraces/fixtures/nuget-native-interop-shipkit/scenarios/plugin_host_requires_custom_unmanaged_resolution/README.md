# Scenario — plugin host requires custom unmanaged resolution

The package works in a plugin-style host only because the host uses an isolated `AssemblyLoadContext` plus explicit unmanaged-library resolution.
This exists to keep the archive honest that ordinary default probing and plugin-host support are different promises.
