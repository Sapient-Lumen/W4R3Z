# rev0091 — nativereentry-oracleseal-preflight

rev0091 adds native oracle seal, native preflight, native re-entry journal, and nativereentryfold so relaunch evidence can only route back toward the load gate while Python fallback remains the authority.

Strong sentence:

> A native relaunch candidate is not load or dispatch permission; it is only a route back to the load gate when Python-oracle, preflight, and re-entry journal memory agree.

This revision stays inside the GCC/native branch but does not expand native authority. It models the seam after native handoff, relaunch gate, and loader seal: how a restart-discovered artifact can be routed back toward the already-existing native load gate without accidentally becoming load or dispatch permission.

New surfaces:

- `nativeoracleseal.py` — Python oracle and fallback memory remain explicit authority.
- `nativepreflight.py` — no-network route-to-load-gate-only marker.
- `nativereentryjournal.py` — restart-sticky memory for the preflight route.
- `nativereentryfold.py` — fold/audit surface for this current path.

Nonclaim: rev0091 still does not load native code, dispatch a native call, implement a production ABI, or touch parsing/crypto/transport/persistence semantics from native code.
