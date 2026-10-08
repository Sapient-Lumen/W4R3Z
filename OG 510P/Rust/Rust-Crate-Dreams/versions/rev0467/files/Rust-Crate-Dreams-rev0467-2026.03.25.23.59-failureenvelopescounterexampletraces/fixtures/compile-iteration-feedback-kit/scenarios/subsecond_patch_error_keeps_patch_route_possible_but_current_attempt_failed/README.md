# Scenario — Subsecond patch route remains valid in theory while the current patch attempt fails

This scenario proves why **patch eligibility** and **live-update outcome** must stay separate.

Subsecond exposes `PatchError` as a public failure surface for patch application, including generic `Dlopen` failure and Android memfd permission failure.
That means a route can still be *the right class of route* (`function_hotpatch`) while the current patch attempt did not apply and old code remains the only honest running story.
