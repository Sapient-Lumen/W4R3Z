# Focused persistence proof build-graph delta

Measured from fresh Debug CMake/Ninja configurations with `ninja -n`.

| Target | Actions | C++ TUs | First-party C++ lines | Core TUs | `sync_domain.cpp` |
|---|---:|---:|---:|---:|:---:|
| peer_ingress_connection_profile rev0788 | 40 | 34 | 52,607 | 26 | yes |
| peer_ingress_connection_profile rev0789 | 6 | 2 | 564 | 0 | no |
| peer_ingress_connection_profile reduction | 85.0% | 94.1% | 98.9% | 100.0% | — |
| canonical_projection_verifier rev0788 | 40 | 34 | 52,549 | 26 | yes |
| canonical_projection_verifier rev0789 | 4 | 2 | 396 | 0 | no |
| canonical_projection_verifier reduction | 90.0% | 94.1% | 99.2% | 100.0% | — |
| sqlite_projection_decoder rev0788 | 40 | 34 | 52,615 | 26 | yes |
| sqlite_projection_decoder rev0789 | 8 | 3 | 850 | 0 | no |
| sqlite_projection_decoder reduction | 80.0% | 91.2% | 98.4% | 100.0% | — |
