# NuGet Native Interop ShipKit fixtures

These fixtures exist to keep the archive honest about what the NuGet shipkit is actually checking.

The core review objects are:
- **RID coverage**
- **loader route**
- **deployment posture**

They exist so the archive does not flatten:
- “the `.nupkg` exists”,
- “the bindings compile”,
- and “the app loaded the DLL on one machine”

into one fake “.NET support” result.
