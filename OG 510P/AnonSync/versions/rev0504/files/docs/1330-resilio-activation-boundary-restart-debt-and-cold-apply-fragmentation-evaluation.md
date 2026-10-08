## Resilio seam evaluation — activation boundary, restart debt, and cold-apply truth

Current official Resilio Sync docs still expose another strong non-clone seam around **activation-boundary truth**.
The important current facts are not subtle:

- `Ignoring files in Sync (Ignore List)` still says IgnoreList is re-read every time it is changed or at `folder_rescan_interval`, yet still recommends a restart if the operator wants the change applied immediately.
- `Setting Delay Time For Syncing` still says FileDelayConfig changes should be saved and then activated by restarting Sync.
- `Collecting debug logs manually` and `Collecting debug logs automatically` still say the operator should turn on debug logging and then restart Sync to make sure the logging posture is actually active.
- `How do I reset my WebUI password?` still says the operator must quit Sync, mutate on-disk settings or config, and restart before the new credentials are authoritative.
- `Sync Service Troubleshooting on Windows` still says some WebUI listen changes require service restart and that a `sync.conf` dropped into the service storage folder is loaded automatically by the service on startup.
- `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` still says remembered global peer addresses can survive until peer-expiration settings are changed and the client is restarted through a burn-down sequence.
- Current Linux/package guidance still says some config and service changes activate on stop/start or enable/start boundaries rather than as hot live edits.

This is strong operational candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `when is this change actually in force, and what stale runtime debt still survives?` still depends on combining IgnoreList, debug-log, WebUI, service-troubleshooting, LAN-only, and Linux/package articles.

So this tranche freezes a stronger replacement line: **mutation locus, activation rung, stale old-world debt, and witness grade become separate modeled truths.**

That is why this revision adds five more first-class pages: **Activation-boundary contract sheet**, **Restart-debt review**, **Applied-state proof**, **Activation timeline**, and **Activation-boundary lineage receipt**.
