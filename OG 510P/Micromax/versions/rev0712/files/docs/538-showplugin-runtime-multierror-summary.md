# Rev597: runtime `showplugin NAME` now keeps multi-error count truth too

`showplugin NAME` is the narrowest post-Enter exact plugin inspector. After rev590, the command-bar exact row already used the calmer `N load errors · last: ...` dialect for one broken plugin with multiple recorded load failures, but the runtime `showplugin NAME` path was still flattening that same state back to only the last error string.

Rev597 keeps the fix tiny and local: `_plugin_showplugin_detail(...)` now keeps the load-error count when `error_count > 1`, so post-Enter `showplugin b` says `errors=2 — 2 load errors · last: secondary issue` instead of `errors=2 — secondary issue`. The goal is simple: exact inspection should not disagree with itself about how many failures Micromax already knows for one plugin.
