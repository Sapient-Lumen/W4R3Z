# Activation pack

`vhk gen-activation-pack <project_dir>` turns planner activation routes plus
host-contract/readiness evidence into a reviewable Linux launch handoff.

It writes:

- `docs/VHK_ACTIVATION_ROUTES.md`
- `docs/VHK_ACTIVATION_FIXUPS.md`
- `docs/VHK_ACTIVATION_PLAN.json`
- `scripts/vhk_review_activation_routes.sh`

The goal is to keep Linux-native wake-up paths explicit:

- launcher/manual fallback is one lane
- compositor/WM bindings are one lane
- portal sessions are one lane
- service-managed text/watcher surfaces are one lane
- remapper/helper daemons are one lane

This pack is intentionally operational rather than magical. It does not claim
that VHK can auto-own every one of those lanes. It keeps route ownership,
fallbacks, and lifecycle seams reviewable.
