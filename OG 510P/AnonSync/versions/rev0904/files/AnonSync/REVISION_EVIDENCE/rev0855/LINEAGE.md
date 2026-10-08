# Rev0855 lineage

Rev0855 is derived only from the sealed rev0854 archive:

`AnonSync-rev0854-2026.07.20.00.11-typedmutexwitness-slotatomic-racegraceful-auditseal.zip`

Archive SHA-256:

`a54e493f3eea8aa8923d5f1815f3ed377eb5bfe1286befde7e8b1c1dae49eeed`

The current rev0855 verifier independently accepted that parent at **26/26 ZIP
checks**. The extracted `AnonSync/` root independently passed **22/22 directory
checks**.

`SOURCE_DIFF_rev0854_to_rev0855.patch` contains only the active implementation
change under `.gitignore`, `CMakeLists.txt`, `include/`, `src/`, `tests/`,
`tools/`, `third_party/`, and `fuzz/`. It applies cleanly to the verified parent.
After replay, every one of the **283** active files matches the rev0855 active
projection, whose digest is:

`5e8dfefbcd798dab45b39efd3a964c902f75d2d6cb5e4dd5f511693fd963f7fb`
