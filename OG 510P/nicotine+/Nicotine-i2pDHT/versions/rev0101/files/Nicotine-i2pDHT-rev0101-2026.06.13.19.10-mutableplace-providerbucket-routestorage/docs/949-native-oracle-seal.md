# Python oracle seal

The Python oracle seal makes the Python reference implementation explicit before any future native reconsideration. It binds loader-seal evidence, artifact/source/fallback/oracle digests, a differential corpus digest, and memory-carriage flags.

It rejects parser bytes, crypto or secret material, transport surfaces, and persistence surfaces. That keeps native code as a leaf optimization and keeps Python as the semantic authority.
