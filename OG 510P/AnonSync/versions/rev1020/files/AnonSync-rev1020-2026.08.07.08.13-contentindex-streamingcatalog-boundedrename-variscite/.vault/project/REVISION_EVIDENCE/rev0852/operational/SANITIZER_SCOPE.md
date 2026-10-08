# Rev0852 sanitizer scope

The focused sanitizer lane used GCC 14.2 with
`-fsanitize=address,undefined`, frame pointers, leak detection, and
halt-on-error behavior. Emitted Ninja compile and link commands were inspected
to confirm both sanitizer families were actually enabled.

Seven focused executables covered the typed policy capsule, raw authorizer
owner, integrated connection authority, transaction exception composition,
allocator-fault cutpoints, process/fork authority, and peer-ingress schema
authority. Result: **992/992** checks.

The bundled SQLite C translation unit remains outside sanitizer
instrumentation under the current build rules. This is focused coverage, not a
full-project sanitizer claim. ThreadSanitizer, MemorySanitizer, Windows,
Release-mode sanitizers, arbitrary concurrent close/use interleavings, and
power-loss behavior were not tested by this lane.
