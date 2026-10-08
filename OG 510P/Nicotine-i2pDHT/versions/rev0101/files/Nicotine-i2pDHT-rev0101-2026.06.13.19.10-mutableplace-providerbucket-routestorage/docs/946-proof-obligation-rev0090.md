# Proof obligation rev0090

For rev0090 to be locally acceptable:

- native handoff must accept only fallback-active relaunch candidates
- relaunch gate must hold until prior native lanes revalidate
- loader seal must preserve tombstone/fallback/quarantine/crash memory
- load and dispatch must remain forbidden throughout the rev0090 path
- native fold spine and native handoff fold must pass
- surface, fold-map, fold-registry, cube-audit, compile, and zip integrity lanes must pass
