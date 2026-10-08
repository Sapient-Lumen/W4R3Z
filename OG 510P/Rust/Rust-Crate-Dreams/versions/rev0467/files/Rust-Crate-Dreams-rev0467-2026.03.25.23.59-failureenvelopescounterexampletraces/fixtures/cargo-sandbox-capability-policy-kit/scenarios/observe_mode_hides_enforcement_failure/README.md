# Scenario: observe mode hides an enforcement failure

A policy run imported from CI reports no hard denials because the backend operated in observe-only mode.
The observed accesses include a network attempt that would have been blocked under enforce mode.

This scenario exists so the kit never lets a green observe run impersonate an enforce-grade support claim.
