# multi_script_sys_delegate

This scenario freezes a small `-sys` style package that has split probe/link logic into two ordered units.

The important property is that order matters:

1. `probe-foo` discovers native paths and writes metadata.
2. `emit-link-flags` consumes that metadata and emits the final link directives.

The bundle should capture that this is a **delegated unit plan**, not merely a prettier build-script log.
