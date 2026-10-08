# Resilio alignment note — 2026-03-08

This note captures the specific product and operational lessons that should influence AnonSync.

## Main takeaways

1. Resilio is the closest public product analogy for folder-centric peer sync and should be imitated aggressively at the UX layer.
2. Resilio's documented sharing model is folder-scoped and permissioned; this supports AnonSync adopting folder + device + permission bundle invites.
3. Resilio's selective-sync / placeholder model is a strong default, especially for mobile.
4. Resilio does not rely solely on filesystem watchers; it documents both immediate filesystem notifications and a default periodic folder rescan every 600 seconds.
5. Resilio's encrypted folders are closer to an encrypted sink / backup node than to a fully symmetric untrusted live peer.
6. Resilio's LAN discovery defaults are useful as a product reference, but its disclosed share-linked beaconing posture should not be copied literally.

## Impact on AnonSync

- Keep Resilio-style permissions and placeholders near the top of the product backlog.
- Treat change detection as a combination of notifications, durable index, and scheduled rescan.
- Stage encrypted sink mode before more ambitious untrusted-peer semantics.
- Keep LAN discovery on by default, but derive beacons from rotating invite tokens rather than stable share identifiers.
