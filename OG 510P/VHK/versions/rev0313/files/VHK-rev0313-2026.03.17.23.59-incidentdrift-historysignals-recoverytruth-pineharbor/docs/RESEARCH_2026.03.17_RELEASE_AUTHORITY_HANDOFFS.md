# Research — release authority handoffs

This note records the ecosystem lesson behind the new setup/release authority work.

## What current Linux tools keep teaching

- desktop portal shortcut lanes are session-bound and mediated by the portal/backend rather than behaving like raw always-on hooks
- user-session services inherit environment and session targets differently from privileged or system-wide helper lanes
- system-wide remappers and uinput helpers are operationally different from launcher/session-only integrations even when they all participate in the same user-visible automation story
- toolchains that keep those boundaries explicit are easier to support, reload, recover, and document honestly

## Product lesson for VHK

VHK should not stop at saying a lane is fast, warm, or shippable. It should also say who owns authority after release:

- launcher/session userland
- desktop-mediated portal/session
- helper-daemon or remapper adjacency
- review-only or mixed surfaces

That lets VHK learn from Linux-native tool ecosystems without copying any one of them wholesale.

## Implemented direction

Revision 0301 carries the authority model into setup, release-lane, release-deploy, and release-stage output so the shipped/operator-facing artifacts keep the same boundary story as the planner.
