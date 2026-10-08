# Scenario — alternate registry trigger intake distinguishes signal from posture

This scenario proves that **P-0535** should not jump directly from imported signals to a new dependency posture.

The workspace is using an alternate registry and an older Cargo toolchain path.
A fresh advisory changes the risk surface, but the correct first artifact is still a **trigger-intake receipt** that keeps separate:
- the imported signal,
- the current anchor/sharedness state,
- and the question of whether to open a transition packet.
