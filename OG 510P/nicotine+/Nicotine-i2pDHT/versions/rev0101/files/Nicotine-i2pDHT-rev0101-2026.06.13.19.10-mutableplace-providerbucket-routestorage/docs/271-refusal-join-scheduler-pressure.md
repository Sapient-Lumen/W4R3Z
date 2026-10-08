# Refusal join scheduler pressure

Useful refusal is capacity evidence, not success. `refusaljoin.py` joins recent refusal-loop evidence with garden scheduling output so a balanced-looking schedule cannot launder repeated refusal-only windows, and a useful-refusal report cannot hide protected-work starvation.

Current decisions include balanced acceptance, watch states, protected starvation quarantine, refusal-loop quarantine, and refusal-without-protected-service quarantine.
