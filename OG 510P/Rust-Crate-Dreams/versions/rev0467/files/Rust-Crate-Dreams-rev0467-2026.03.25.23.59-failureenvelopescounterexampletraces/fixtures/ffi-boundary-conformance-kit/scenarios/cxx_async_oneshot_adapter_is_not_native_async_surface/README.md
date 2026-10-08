# Scenario — CXX async oneshot adapter is not a native async surface

This scenario models CXX's documented async workaround.

CXX says direct async FFI is in scope but not implemented yet.
The documented path uses an opaque Rust context plus a oneshot callback adapter. The review objects therefore need to say this is **adapter-mediated**, not native async support.
