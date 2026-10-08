# rev0033 audit/refactor notes

Added `tools/routing_family_report.py` to separate route-selection, route-coordination, self-routing, and attribution/geometry guard fields.

The cube should not promote router claims unless the relevant probe records random-router baselines, dense/simple baselines, rare-token/rare-route misses, and route-shift/deployment costs.
