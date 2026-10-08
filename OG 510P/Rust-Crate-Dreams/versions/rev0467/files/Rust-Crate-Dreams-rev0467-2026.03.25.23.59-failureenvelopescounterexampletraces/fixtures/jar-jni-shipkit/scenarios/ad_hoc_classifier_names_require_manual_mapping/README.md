# Scenario: ad hoc classifier names require manual mapping

The package publishes attached native artifacts, but uses project-local classifier strings instead of a detector-friendly OS/arch/libc dialect.
Downstream consumers can still wire the dependency up manually, but the support contract should not pretend classifier intake is boring.
