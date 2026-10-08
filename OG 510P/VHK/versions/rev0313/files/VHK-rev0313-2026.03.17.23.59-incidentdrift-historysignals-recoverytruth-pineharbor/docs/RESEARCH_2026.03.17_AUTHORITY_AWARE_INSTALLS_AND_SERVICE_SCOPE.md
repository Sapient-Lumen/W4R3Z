# Research — authority-aware installs and service scope

This note records the ecosystem lesson behind the new authority-aware install/service work.

## What other Linux tools keep teaching us

- text expansion tools are often resident **services** with their own config/runtime trees and lifecycle controls
- desktop-portal shortcut lanes are **session/catalog** objects rather than generic raw hotkey hooks
- X11-era automation tools still matter, but they are often explicit about their protocol boundary instead of pretending to be universal
- uinput/virtual-device injectors often rely on a **persistent daemon** or privileged helper state
- system-wide remappers usually live as dedicated daemons at the evdev/uinput edge

## Product lesson for VHK

A Linux-native pseudoclone of AHK should not flatten those differences into one giant “works on Linux” checkbox. It should let authors compose several honest lanes:

- launcher/userland lane
- resident session-service lane
- desktop-mediated portal lane
- adjacent helper/remapper lane

That lets VHK stay creative without becoming vague. The runner can still unify authoring, planning, and review, but shipping/install artifacts must preserve the ownership boundary that each lane implies.

## Implemented direction

Revision 0300 turns that lesson into concrete handoff behavior:

- native-install outputs now compute an authority policy from project/planner signals
- service-composition outputs now inherit that policy and declare their service scope
- installed app trees now carry a packaged authority guide so the boundary survives after deployment
