# Revision 0300 — authority-aware installs and service scope

This revision makes native-install and session-service generation consume Linux authority boundaries directly instead of leaving that insight trapped in planner review docs.

## What changed

- `build_native_install_plan()` now derives `authority_policy` from project/planner signals
- native-install docs now render **Authority ownership policy**
- generated native app trees now ship `VHK_AUTHORITY_OVERVIEW.md`
- native desktop entries now expose an `OpenAuthorityGuide` quick action
- `build_service_compose_plan()` now carries `authority_scope`, `authority_policy`, and explicit session-owned surface ids
- service-composition docs now render **Authority ownership and service scope**

## Why it matters

The previous planner work identified ownership boundaries, but install/service handoffs still risked implying that a launcher or user unit somehow owned portal sessions, remapper edges, or privileged helpers too. This revision keeps those lines explicit in the artifacts operators actually install and run.

## Test coverage

- `tests/test_native_install_pack_cli.py`
- `tests/test_service_compose_pack_cli.py`
