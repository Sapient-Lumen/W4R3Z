# Research notes — rev0965

A bounded selection algorithm does not by itself impose a traversal-wide bound when recursion retains caller-owned batches. The corrected ownership rule is stronger: at most one selected-name batch may exist across the resumable traversal, and that invariant is checked both before selector allocation and by an RAII owner around each batch lifetime.

Releasing parent storage trades memory for repeated enumeration. Since POSIX directory iteration is asynchronous rather than a point-in-time namespace snapshot, continuation cannot infer unchanged membership merely from a previously charged count. Rev0965 therefore compares the exact unconsumed suffix cardinality before processing a rescan and conservatively withholds completion on detected cardinality drift. Equal-cardinality replacement and mutation after the final required pass remain watcher/later-epoch work, which is recorded as a nonclaim rather than hidden.
