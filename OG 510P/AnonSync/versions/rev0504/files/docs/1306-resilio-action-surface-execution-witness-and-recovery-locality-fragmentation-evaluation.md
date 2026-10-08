## Resilio seam evaluation — action surface, witness locality, and recovery-scope truth

Current official Resilio Sync docs still expose another strong non-clone seam around **action-surface truth**.
The important current facts are not subtle:

- `Configuring WebUI` still says WebUI is the default and only UI path on Linux/NAS and the default UI path on Windows when Sync is installed as a service.
- `Folder Preferences` still says that folder-level preferences are available on desktop platforms only.
- `Power user preferences` still says `disable_remove_from_all_devices` is ignored in Linux WebUI.
- `Using Archive for file versioning and restoring deleted files` still says `Open Archive` is available from desktop Sync UI but not WebUI, that WebUI and Android must use the file browser instead, and that Archive is not accessible on iOS.
- `Updating Sync to latest version` still says manual `Check now` update checking is not available in WebUI.
- `Sharing a folder locally` still says local shares are supported only on desktop versions.
- `Does Sync work in background?` and `Sync for iOS Peculiarities` still say desktop and Android can continue in background while iOS transfer requires the app to be open.

This is strong operational candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `can I do this here, can I only verify it elsewhere, and where does recovery actually live?` still depends on combining desktop UI docs, WebUI docs, platform-peculiarity pages, folder-settings pages, and troubleshooting notes.

So this tranche freezes a stronger replacement line: **execution surface, inspection surface, recovery surface, out-of-band surface, and absent surface become separate modeled truths.**

That is why this revision adds five more first-class pages: **Action-surface contract sheet**, **Surface-locality review**, **Action-availability proof**, **Surface-shift timeline**, and **Action-surface lineage receipt**.
