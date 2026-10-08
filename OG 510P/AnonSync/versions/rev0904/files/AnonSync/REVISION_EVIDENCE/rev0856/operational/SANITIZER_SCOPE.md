# Sanitizer scope

GCC 14.2 built and ran the three rev0856-focused targets with AddressSanitizer and UndefinedBehaviorSanitizer. Runtime options enabled leak detection and halt/abort on first error. The three targets passed **659/659** checks.

Generated Ninja commands show `-fsanitize=address,undefined` on the focused C++ compile and final executable link commands. The bundled SQLite C amalgamation was not instrumented. No full-project sanitizer, ThreadSanitizer, Release-mode, or Windows-runtime claim is made.
