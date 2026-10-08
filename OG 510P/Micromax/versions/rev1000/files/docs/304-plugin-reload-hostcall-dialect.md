# Plugin reload hostcall dialect

Rev362 tightens one small but important trust seam: the live Micromax hostcall `plugin.reload` now reuses the same reload-feedback helper as the command-bar `plugin reload NAME` path.

Why this matters:
- Micromax is supposed to become the editor's live scripting environment, not a second-class side channel
- once command-bar reload became explicit about post-reload state, broken known plugins, and unknown names, hostcall reload was the remaining path still speaking an older generic `plugin reload error: ...` dialect
- that made script-driven reloads less inspectable than the editor surface they are meant to power

New rule:
- successful hostcall reloads report the post-reload plugin summary (`plugin reload: name [...]`)
- broken known plugins start with that same summary and list current recorded load errors directly
- unknown names fail plainly as `plugin reload: no such plugin: NAME`

Implementation note:
- reload feedback now lives in one shared editor helper so command-bar and hostcall paths do not drift again
Rev390 follow-up:
- absent plugin-manager reloads now fail just as explicitly as missing-plugin reloads: `plugin reload: no plugin manager`
- because hostcall reload still reuses the shared helper, command-bar and Micromax hostcall reload stay in lockstep for this boundary too
