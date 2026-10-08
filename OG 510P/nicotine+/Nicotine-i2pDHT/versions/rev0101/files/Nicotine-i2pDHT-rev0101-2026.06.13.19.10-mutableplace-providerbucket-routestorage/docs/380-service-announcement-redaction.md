# Service announcement redaction

A service catalog is local truth about what a garden is willing to do, but a
service announcement is only an entrance hint. rev0037 adds a redacted
announcement capsule so a garden can publish a small, time-bounded subset of its
accepted catalog without leaking the whole service surface.

Pressure rules:

- signatures, sequence, replay, rollback, fork, TTL, and validity windows are
  checked before an announcement can seed entrances;
- public announcements may only expose catalog services that were explicitly
  marked public;
- bridge gateway announcements are locally disabled by default;
- labels are represented as fixed-size redacted digests, not raw destinations,
  interests, filenames, or content keys;
- noisy hint counts and bulk-provider public exposure are held under low/normal
  metadata posture.

The announcement is not a permission. It must still pass ingressgate and later
service ticket boundaries before handler work happens.
