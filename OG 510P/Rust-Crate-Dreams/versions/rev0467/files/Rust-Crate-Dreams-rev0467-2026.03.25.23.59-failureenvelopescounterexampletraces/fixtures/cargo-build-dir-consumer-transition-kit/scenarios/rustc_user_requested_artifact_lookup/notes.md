# rustc user-requested artifact lookup

This scenario exists to keep the crate from overclaiming.
Sometimes a helper wants a user-requested artifact and currently scrapes compiler-oriented locations.
The right answer may be a final-artifact handoff, or it may still be an upstream gap. The bundle should preserve which one it is.
