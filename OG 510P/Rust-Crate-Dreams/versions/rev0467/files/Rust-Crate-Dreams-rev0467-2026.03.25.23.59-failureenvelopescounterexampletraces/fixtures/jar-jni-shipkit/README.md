# JAR/JNI Native ShipKit fixtures

Fixture families now focus on three sharper review objects:
- **classifier dialect** — whether published classifier names align with a downstream-friendly `os.detected.classifier`-style intake or require project-local mapping
- **native-access posture** — whether the release honestly declares `--enable-native-access` expectations for class-path or module-path consumers
- **loader residency** — whether the native library is expected via `java.library.path`, extraction to a temp location, absolute-path loading, or manual installation

Scenario families:
- `ad_hoc_classifier_names_require_manual_mapping/` — classifier artifacts exist, but their naming scheme is too custom for ordinary detector-based intake
- `classpath_loader_needs_all_unnamed_but_docs_omit_it/` — a class-path loader uses restricted native access but package docs fail to declare the required runtime posture
- `extract_then_load_temp_policy_ambiguous/` — the package extracts a native library and loads it, but temp residency and cleanup policy are not honestly documented
