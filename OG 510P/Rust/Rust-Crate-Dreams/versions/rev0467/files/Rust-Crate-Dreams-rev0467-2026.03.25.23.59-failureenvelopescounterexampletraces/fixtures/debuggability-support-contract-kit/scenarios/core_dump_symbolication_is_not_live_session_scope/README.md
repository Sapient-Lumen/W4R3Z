# core_dump_symbolication_is_not_live_session_scope

This scenario shows why a post-mortem stack walk or symbolication lane must not be flattened into a live interactive-debugging claim.
The point is not that post-mortem work is weak; it is that it is a **different session scope** with a different claim ceiling.
