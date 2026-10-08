# `spawn_blocking` queues after thread-cap scenario

Focus: Tokio `spawn_blocking` keeps spawning blocking threads until the configured upper limit is reached, then puts additional work in a queue.

Resource-surface reading: the crate may have a configurable worker cap while still exposing queued backlog growth after saturation. Pressure signals should call out blocking-thread count and blocking-queue depth rather than pretending the cap alone settles capacity posture.
