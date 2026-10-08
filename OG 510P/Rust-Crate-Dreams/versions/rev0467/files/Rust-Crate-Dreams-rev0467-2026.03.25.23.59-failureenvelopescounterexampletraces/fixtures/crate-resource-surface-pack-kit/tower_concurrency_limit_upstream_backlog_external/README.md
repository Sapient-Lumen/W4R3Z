# Tower concurrency-limit with external backlog scenario

Focus: Tower concurrency limits bound the number of requests concurrently processed by the wrapped service, but that alone does not fully specify where upstream waiting, buffering, or admission happens.

Resource-surface reading: `externally_bounded` or `manual_review_required` is often the honest posture for upstream backlog unless the crate also publishes its own queue / timeout / shedding contract.

This scenario now also anchors **backlog ownership** and **admission path** truth, not just the existence of a concurrency limit.
