# Parent home manifest poisoning

This scenario captures the class where a parent `Cargo.toml` unexpectedly changes workspace discovery for a subproject.
The bundle should prove the probed parents instead of only repeating Cargo’s final error.
