# ADR 0077 — Provider compatibility before legacy wrapper

Status: accepted in rev0018.

The legacy `providerpoison.py` surface should not be silently aliased or deleted until legacy-only names are classified as canonical reexports, adapters, historical-only constants, or manual decisions.
