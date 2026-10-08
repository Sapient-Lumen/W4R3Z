# Cooperation benchmark programs should publish direct role-annotated primary-open targets for compact-card reentry

When a compact-card stack already publishes ordered open paths and role-annotated target families, one small reentry burden still remains: the inheritor has to scan that family to recover the one canonical first-open object.

Keep one direct witness explicit instead:

- publish `focus_primary_open_target` on the main compact-card reentry surfaces;
- publish `primary_open_target` on lineage-local handoff packs;
- require those direct witnesses to equal the first item of the corresponding ordered target family rather than introducing a second browsing semantics.

This keeps the archive small while removing one more local reconstruction step for future inheritors.
