# Scenario — registry TP-only state must be imported, not assumed

A repository still carries mixed-mode planning text, but crates.io has already enabled **Trusted Publishing Only Mode** for the published package.
The lane should emit an imported registry-state artifact rather than assuming repo-local policy remains authoritative.
