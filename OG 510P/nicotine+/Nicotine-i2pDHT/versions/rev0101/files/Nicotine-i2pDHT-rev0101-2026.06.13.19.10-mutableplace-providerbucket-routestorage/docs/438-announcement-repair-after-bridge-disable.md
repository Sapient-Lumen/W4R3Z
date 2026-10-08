# Announcement repair after bridge disable

Disabling a public bridge is not enough if stale public announcements continue to circulate. rev0042 adds a repair lane that requires public withdrawal and successor catalog evidence before a garden treats the service as repaired.

`AnnouncementRepairSignal` records bridge disable, public withdrawal, successor catalog, private announcement, stale public announcement, and tombstone scan signals. The lane binds every signal to service, scope, catalog digest, announcement digest, bridge-disable digest, family, freshness, and signature.

Current risky cases tested:

- repair accepts bridge-disable + public-withdrawal + successor-catalog + tombstone-scan evidence;
- stale public announcement evidence quarantines;
- successor catalog rollback quarantines;
- same-sequence successor catalog fork quarantines;
- one-family repair evidence holds;
- signature failure, replay, expiry/future time, service drift, scope drift, and hard-negative pressure are modeled.

Design guess: public bridge disable should be treated as a negative-evidence event that triggers catalog/announcement repair, not as a local toggle that magically erases network memory.
