# Handler quench and cooldown

`handlerquench.py` models repeated inbound handler attempts that are not catastrophic one at a time but become dangerous in a window.

The quench lane tracks accepted attempts, hold/watch decisions, useful-refusal loops, raw-key metadata pressure, hard negatives, family/path diversity, and exact caller/handler/scope/request binding.

It can allow a healthy window, hold under low diversity, cool down almost-passing loops, cool down refusal-only loops, quench raw-key pressure, or quarantine replay and drift.

This is local pressure only. It is not global reputation and not a ban list.
