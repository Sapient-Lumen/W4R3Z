# Route selection pack

`vhk gen-route-selection-pack <project_dir>` turns activation routes plus
host-contract/readiness evidence into an explicit **reference-route decision**.

It writes:

- `docs/VHK_ROUTE_SELECTION.md`
- `docs/VHK_ROUTE_FIXUPS.md`
- `docs/VHK_ROUTE_PLAN.json`
- `scripts/vhk_review_route_selection.sh`

The goal is to keep one shipping story visible per activation lane instead of
flattening every route into an undifferentiated list. The pack chooses:

- one universal/manual wake-up route
- one preferred trigger route
- one preferred text-surface route (when relevant)
- one preferred event-plane route (when relevant)
- one preferred helper/input-edge route (when relevant)

It also keeps healthier fallbacks visible so operators can promote them when the
design-preferred route is still only planned or degraded.
