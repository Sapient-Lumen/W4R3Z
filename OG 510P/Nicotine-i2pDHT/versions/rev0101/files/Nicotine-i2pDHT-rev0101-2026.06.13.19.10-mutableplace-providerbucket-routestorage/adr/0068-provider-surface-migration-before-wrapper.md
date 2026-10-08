# ADR 0068 — provider surface migration before wrapper

`provider_poison.py` is the canonical current provider memory/quarantine surface. `providerpoison.py` remains legacy while historical tests still import it. The cube must scan and migrate/adapt callers before converting the legacy module into a compatibility wrapper.

Status: accepted for rev0016 audit/refactor surface.
