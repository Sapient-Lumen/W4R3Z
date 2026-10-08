# cap-std profile blocks absolute-path escape

Focus: a crate offers a capability-oriented `Dir`-based profile, but an internal helper still canonicalizes or opens an absolute path through an ambient API.
This fixture exists to prove that using capability substrate in some places is not the same as a fully witnessed `sandbox_ready` profile.
