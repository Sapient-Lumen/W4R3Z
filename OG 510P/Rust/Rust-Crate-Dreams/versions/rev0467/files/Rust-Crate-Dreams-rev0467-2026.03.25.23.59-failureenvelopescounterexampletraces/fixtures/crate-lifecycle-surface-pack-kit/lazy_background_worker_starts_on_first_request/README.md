# Lazy background worker starts on first request

Simulates a client crate that looks cheap to construct, but starts a reconnect / housekeeping worker on the first real request.
The lifecycle contract should not blur “construction succeeds” with “background work has begun”.

Why this matters:
- many SDK / client crates defer task creation until the first request or subscription;
- downstream users need to know whether merely holding a handle is inert or whether using it once changes shutdown obligations;
- a lifecycle-surface crate should therefore model **activation boundaries**, not just a flat worker inventory.

What this scenario should force:
- an explicit activation class such as `first_use_lazy`
- a background-work receipt that names the lazy worker
- a summary note that shutdown obligations begin only after first use
- a doctor warning such as `background_work_starts_before_user_opt_in` when the pack overclaims constructor inertness
