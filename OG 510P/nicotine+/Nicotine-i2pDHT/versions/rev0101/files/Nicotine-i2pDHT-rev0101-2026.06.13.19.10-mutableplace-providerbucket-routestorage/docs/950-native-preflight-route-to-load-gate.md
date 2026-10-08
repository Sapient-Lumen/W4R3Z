# Native preflight route-to-load-gate

Native preflight is deliberately weaker than load permission. It only says that handoff, relaunch gate, loader seal, and Python-oracle seal agree at one exact boundary, so a later lane may ask the existing native load gate again.

It forbids native load and dispatch attempts. If an implementation tries to treat relaunch evidence as dispatch permission, the preflight quarantines.
