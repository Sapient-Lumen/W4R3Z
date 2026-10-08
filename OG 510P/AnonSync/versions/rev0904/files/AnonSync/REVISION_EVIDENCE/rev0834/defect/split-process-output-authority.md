# Defect: PID and evidence-stream authority were split

A child PID, stdout descriptor, stderr descriptor, byte budget, wait status, and
timeout describe one evidence-producing transition. Treating them as unrelated
locals allows failure on one path to strand authority owned by another.

Rev0834 makes them one move-only owner. Move assignment and destruction consume
displaced authority; timeout, overflow, read, poll, allocation, and wait failure
kill/reap and close before throwing; status mismatch is reported only after both
streams reach EOF and the leader is reaped.
