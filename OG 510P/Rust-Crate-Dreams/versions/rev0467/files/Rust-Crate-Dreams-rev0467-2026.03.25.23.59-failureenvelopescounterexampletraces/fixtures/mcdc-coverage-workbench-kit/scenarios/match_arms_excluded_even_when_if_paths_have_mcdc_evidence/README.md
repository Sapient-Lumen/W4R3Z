# Scenario — match arms excluded even when nearby `if` paths have MC/DC evidence

This scenario protects the distinction between **local MC/DC-looking evidence** and **full decision inventory authority**.

The toolchain may support `if` / `while` / lazy-bool paths while still lacking full support for individual `match` arms and or-patterns.
The crate must therefore record a conservative decision-authority receipt instead of implying that the entire function body was covered at MC/DC strength.
