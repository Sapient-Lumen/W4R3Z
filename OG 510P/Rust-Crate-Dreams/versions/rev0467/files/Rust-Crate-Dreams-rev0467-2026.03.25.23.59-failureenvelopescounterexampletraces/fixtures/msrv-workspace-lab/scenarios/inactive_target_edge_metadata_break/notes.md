# Inactive target edge raises metadata floor

This scenario captures the class where the main build lane stays green, but an inactive target-specific dependency edge still raises pressure elsewhere.
The bundle must keep `build` and `metadata` lanes separate.
