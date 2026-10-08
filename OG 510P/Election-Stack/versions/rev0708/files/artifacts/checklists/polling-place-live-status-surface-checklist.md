# Polling-place live-status surface checklist

- Name one authoritative public path for same-day site status and one authoritative help path.
- Publish a small, explicit status vocabulary for `normal`, `high_demand`, `delayed_open`, `degraded_service`, `rerouted`, `closed`, and `superseded` states where applicable.
- Use coarse queue-advisory buckets or similarly bounded terms; do not imply false-precision predictions.
- Publish effective timestamps for delayed openings, reroutes, degraded-service notices, and recovery notices.
- Treat same-day disruptions and reroutes as explicit superseding notices, not silent edits.
- Distinguish queue advisories from law-governing cutoff rules; if line-close guidance is published, make it explicit and timestamped.
- Check parity across website, map/listing surface, hotline/help script packet, signage packet, social posts, and signed notices.
- Publish accessible and translated versions where required, plus the fallback path when the primary site or live-status endpoint fails.
- Name the replacement site, alternate time/path, or official help contact whenever a change affects voter actionability.
- Do not publish minute-by-minute turnout streams, staffing rosters, security details, or internal incident channels.
- Record `last_verified_at` and the latest correction notice pointer.
