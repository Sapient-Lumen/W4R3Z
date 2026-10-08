# Sanitizer scope for AnonSync rev0870

The GCC 14 sanitizer build uses Debug configuration with warnings as errors,
AddressSanitizer and UndefinedBehaviorSanitizer enabled, leak detection enabled,
and halt-on-error behavior. `ANONSYNC_SANITIZE_BUNDLED_SQLITE=ON`, so the bundled
SQLite amalgamation used by the focused owner is included rather than silently
remaining uninstrumented.

Seven focused executables pass: network model, hash graph/projection, allocation
atomicity, aggregate budget, capacity/backpressure, outbox lease, and SQLite
owner. Together they report 2,198 checks. The owner is also run separately after
the first combined command-window interruption; the final CTest lane passes all
seven in 23.45 seconds.

This is not a full-project sanitizer claim. It does not include ThreadSanitizer,
all integrated core paths, every third-party configuration, Windows, or a
qualified physical power-loss environment.
