# build_analysis_import_only

This tiny scenario exists to prove a crate boundary:

- Cargo nightly can record and replay build-analysis sessions.
- **P-0469** should freeze those evolving inputs into a smaller stable bundle for support workflows.

The point is not to out-Cargo Cargo.
The point is to export one conservative, redactable artifact another human can review.
