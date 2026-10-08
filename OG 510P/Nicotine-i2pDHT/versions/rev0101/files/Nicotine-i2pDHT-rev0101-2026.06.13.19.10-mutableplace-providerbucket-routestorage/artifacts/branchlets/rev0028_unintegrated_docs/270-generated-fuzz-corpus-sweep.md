# Generated fuzz corpus sweep

rev0028 grows the deterministic malformed-input lane from hand-written cases into a tiny generated corpus. The goal is not production fuzzing; it is pressure before live I2P/SAM bytes exist.

The generator starts from accepted fuzzwire seeds and creates rejection cases for parser trailing data, duplicate keys, depth bombs, wire payload append/truncate, and shadow expected-digest drift. The useful invariant is simple: every generated mutation should reject for the class it claims to test.

This keeps parser, canonical wire, and shadow-report boundaries tied together instead of letting each one pass in isolation.
